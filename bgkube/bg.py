from six import add_metaclass
from time import sleep

from bgkube import cmd, registries
from bgkube.api import KubeApi
from bgkube.run import Runner
from bgkube.errors import ActionFailedError
from bgkube.utils import output, log, timestamp, require, get_loadbalancer_address, is_host_up


class BgKubeMeta(type):
    required = [
        'cluster_zone', 'cluster_name', 'image_name', 'service_name', 'service_config', 'deployment_config'
    ]
    optional = [
        'context', 'dockerfile', 'env_file', 'smoke_tests_command', 'smoke_service_config', 'docker_machine_name',
        'db_migrations_job_config_seed', 'db_migrations_status_command', 'db_migrations_apply_command',
        'db_migrations_rollback_command', 'kops_state_store', 'container_registry', 'service_timeout',
        'smoke_service_timeout', 'deployment_timeout', 'db_migrations_job_timeout'
    ]
    optional_defaults = {
        'context': '.',
        'dockerfile': './Dockerfile',
        'container_registry': registries.DEFAULT,
        'service_timeout': 120,
        'smoke_service_timeout': 120,
        'deployment_timeout': 120,
        'db_migrations_job_timeout': 120
    }

    def __new__(mcs, name, bases, attrs):
        attrs['required'] = mcs.required
        attrs['optional'] = mcs.optional

        for field in mcs.required + mcs.optional:
            attrs[field] = mcs.optional_defaults.get(field, None)

        return super(BgKubeMeta, mcs).__new__(mcs, name, bases, attrs)


@add_metaclass(BgKubeMeta)
class BgKube(object):
    def __init__(self, options):
        self.load_options(options)

        self.kube_api = KubeApi()
        self.runner = Runner(cmd.DOCKERMACHINE_EVAL_ENV.format(self.docker_machine_name))
        self.registry = registries.load(self.runner, options)

    def load_options(self, options):
        for opt in self.required:
            setattr(self, opt, require(options, opt))

        for opt in self.optional:
            setattr(self, opt, getattr(options, opt, None) or getattr(self, opt))

    @log('Building image {image_name} using {dockerfile}...')
    def build(self):
        tag = timestamp()
        self.runner.start(cmd.DOCKER_BUILD.format(
            context=self.context,
            dockerfile=self.dockerfile,
            image=self.image_name,
            tag=tag,
        ))

        return tag

    @log('Pushing image {image_name}:{tag} to {registry}...')
    def push(self, tag):
        self.registry.push('{}:{}'.format(self.image_name, tag))

    @log('Applying {_} using config: {filename}...')
    def apply(self, _, filename, tag=None, color=''):
        return self.kube_api.apply(filename, self.env_file, TAG=tag, COLOR=color, ENV_FILE=self.env_file)

    def pod_find(self, tag, color):
        results = [pod for pod in self.kube_api.pods(tag=tag, color=color) if pod.ready]
        return results[0] if results else None

    def pod_exec(self, tag, color, command, *args):
        pod = self.pod_find(tag, color).name
        return self.runner.start(cmd.KUBECTL_EXEC.format(pod=pod, command=command, args=' '.join(args)), capture=True)

    def migrate_initial(self, tag):
        if self.db_migrations_job_config_seed:
            def job_completions_extractor(job):
                completions = job.obj['spec']['completions']
                succeeded_completions = job.obj['status']['succeeded']

                return completions if succeeded_completions == completions else None

            applied_objects = self.apply('db migration', self.db_migrations_job_config_seed, tag=tag)
            self.wait_for_resource_running(
                'Job',
                'completions',
                job_completions_extractor,
                self.db_migrations_job_timeout,
                *applied_objects
            )

    def migrate_apply(self, tag, color):
        previous_state = None

        if self.db_migrations_status_command:
            previous_state = self.pod_exec(tag, color, self.db_migrations_status_command)

        if self.db_migrations_apply_command:
            self.pod_exec(tag, color, self.db_migrations_apply_command)

        return previous_state

    def migrate_rollback(self, tag, color, previous_state):
        if self.db_migrations_rollback_command:
            self.pod_exec(tag, color, self.db_migrations_rollback_command, previous_state)

    def migrate(self, tag, color):
        db_migrations_previous_state = None
        is_initial = self.active_env() is None

        if is_initial:
            self.migrate_initial(tag)
        else:
            db_migrations_previous_state = self.migrate_apply(tag, color)

        return is_initial, db_migrations_previous_state

    def active_env(self):
        service = self.kube_api.resource_by_name('Service', self.service_name)
        return None if not service else service.obj['spec']['selector']['color']

    def other_env(self):
        return {
            'blue': 'green',
            'green': 'blue'
        }.get(self.active_env(), None)

    def deploy(self, tag):
        color = self.other_env() or 'blue'
        applied_objects = self.apply('deployment', self.deployment_config, tag=tag, color=color)

        self.wait_for_resource_running(
            'Deployment',
            'replicas',
            lambda deployment: deployment.replicas if deployment.ready and self.pod_find(tag, color) else None,
            self.deployment_timeout,
            *applied_objects
        )

        return color

    @log('Waiting for {resource_type} {prop} to become available')
    def wait_for_resource_running(self, resource_type, prop, prop_extractor, timeout_seconds, *object_names):
        def try_extract_value(resource_name):
            try:
                result = self.kube_api.resource_by_name(resource_type, resource_name)
                return prop_extractor(result or {})
            except (IndexError, KeyError, AttributeError):
                return None

        def extract_value_with_timeout(resource_name):
            value = None

            if timeout_seconds:
                attempts = 0

                while not value and attempts < timeout_seconds:
                    sleep(1)
                    attempts += 1
                    output('.', '', flush=True)
                    value = try_extract_value(resource_name)
            else:
                value = try_extract_value(resource_name)

            if value:
                output('\n{} {} {} is: {}'.format(resource_type, resource_name, prop, value))
            elif timeout_seconds:
                raise ActionFailedError(
                    '\nFailed after {} seconds elapsed. For more info try running: $ kubectl describe {} {}'.format(
                        timeout_seconds, resource_type, resource_name))

            return value

        values = [extract_value_with_timeout(name) for name in object_names]
        return values

    @log('Running smoke tests on {color} deployment...')
    def smoke_test(self, color):
        if self.smoke_service_config:
            def service_host_extractor(service):
                service_address = get_loadbalancer_address(service)
                return service_address if is_host_up(service_address) else None

            applied_objects = self.apply('smoke service', self.smoke_service_config, color=color)
            smoke_service_address = ','.join(self.wait_for_resource_running(
                'Service',
                'host',
                service_host_extractor,
                self.smoke_service_timeout,
                *applied_objects
            ))

            return_code = self.runner.start(self.smoke_tests_command, TEST_HOST=smoke_service_address, silent=True)
            return return_code == 0

        return True

    @log('Promoting {color} deployment...')
    def swap(self, color):
        self.apply('public service', self.service_config, color=color)
        self.wait_for_resource_running(
            'Service',
            'status',
            lambda service: 'ready' if service.exists(ensure=True) else None,
            self.service_timeout,
            self.service_name
        )

    @log('Publishing...')
    def publish(self):
        next_tag = self.build()
        self.push(next_tag)

        next_color = self.deploy(next_tag)
        is_initial, db_migrations_previous_state = self.migrate(next_tag, next_color)
        health_ok = self.smoke_test(next_color)

        if health_ok:
            self.swap(next_color)
        else:
            if not is_initial:
                self.migrate_rollback(next_tag, next_color, db_migrations_previous_state)

            raise ActionFailedError('Cannot promote {} deployment because smoke tests failed'.format(next_color))

        output('Done.')

    @log('Rolling back to previous deployment...')
    def rollback(self):
        color = self.other_env()

        if color:
            self.swap(color)
        else:
            raise ActionFailedError('Cannot rollback to a previous environment because one does not exist.')

        output('Done.')

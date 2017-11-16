from six import add_metaclass
from time import sleep

from bgkube import cmd
from bgkube.api import KubeApi
from bgkube.run import Runner
from bgkube.errors import ActionFailedError
from bgkube.registries import GoogleContainerRegistry
from bgkube.utils import output, log, timestamp, require


class BgKubeMeta(type):
    required = [
        'cluster_zone', 'cluster_name', 'image_name', 'service_name', 'service_config',
        'deployment_name', 'deployment_config'
    ]
    optional = [
        'context', 'dockerfile', 'env_file', 'smoke_service_name', 'smoke_tests_command', 'smoke_service_config',
        'docker_machine_name', 'db_migrations_job_config_seed', 'db_migrations_status_command',
        'db_migrations_apply_command', 'db_migrations_rollback_command'
    ]
    optional_defaults = {
        'context': '.',
        'dockerfile': './Dockerfile'
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
        self.container_registry = GoogleContainerRegistry(self.runner, self.cluster_name, self.cluster_zone)

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

    @log('Pushing image {image_name}:{tag} to {container_registry}...')
    def push(self, tag):
        self.container_registry.push('{}:{}'.format(self.image_name, tag))

    @log('Applying {_} using config: {filename}...')
    def apply(self, _, filename, tag=None, color=''):
        self.kube_api.apply(filename, self.env_file, TAG=tag, COLOR=color)

    def pod_exec(self, tag, color, command, *args):
        pod = [pod for pod in self.kube_api.pods(tag=tag, color=color) if pod.ready][0].name
        return self.runner.start(cmd.KUBECTL_EXEC.format(pod=pod, command=command, args=' '.join(args)), capture=True)

    def migrate_initial(self, tag):
        if self.db_migrations_job_config_seed:
            self.apply('db migration', self.db_migrations_job_config_seed, tag=tag)

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
        service = self.kube_api.service(self.service_name)
        return None if not service else service.obj['spec']['selector']['color']

    def other_env(self):
        return {
            'blue': 'green',
            'green': 'blue'
        }.get(self.active_env(), None)

    def deploy(self, tag):
        def extractor(result):
            status = result.obj['status']

            if status['availableReplicas'] == status['readyReplicas'] == status['updatedReplicas'] == result.replicas:
                return result.replicas

            return None

        color = self.other_env() or 'blue'
        target_deployment_name = '{}-{}'.format(self.deployment_name, color)

        self.apply('deployment', self.deployment_config, tag=tag, color=color)
        self.wait_for_object_prop('deployment', target_deployment_name, 'replicas', extractor)

        return color

    @log('Waiting for {entity} {name} {prop} to become available')
    def wait_for_object_prop(self, entity, name, prop, extractor, max_attempts=100):
        attempts = 0
        value = None

        while not value and attempts < max_attempts:
            output('.', '', flush=True)
            result = getattr(self.kube_api, entity)(name)

            try:
                value = extractor(result or {})
            except KeyError:
                pass
            finally:
                sleep(1)
                attempts += 1

        if value:
            output('\n{} {} {} is: {}'.format(entity, name, prop, value))
            return value

        raise ActionFailedError('Timed out while waiting for service {} after {} attempts'.format(name, max_attempts))

    @log('Running smoke tests on {color} deployment...')
    def smoke_test(self, color):
        if self.smoke_service_config:
            def extractor(result):
                return result.obj['status']['loadBalancer']['ingress'][0]['ip']

            self.apply('smoke service', self.smoke_service_config, color=color)
            service_external_ip = self.wait_for_object_prop('service', self.smoke_service_name, 'ip', extractor)

            return_code = self.runner.start(self.smoke_tests_command, TEST_HOST=service_external_ip, silent=True)
            return return_code == 0

        return True

    @log('Promoting {color} deployment...')
    def swap(self, color):
        self.apply('public service', self.service_config, color=color)

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

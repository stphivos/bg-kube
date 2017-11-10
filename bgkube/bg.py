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
        'deployment_config'
    ]
    optional = [
        'context', 'dockerfile', 'env_file', 'smoke_service_name', 'smoke_tests_command', 'smoke_service_config',
        'db_migration_job_config', 'docker_machine_name'
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
            setattr(self, opt, getattr(options, opt, getattr(self, opt)))

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

    def migrate(self, tag):
        if self.db_migration_job_config:
            self.apply('db migration', self.db_migration_job_config, tag=tag)

    def active_env(self):
        service = self.kube_api.service(self.service_name)
        return None if not service else service.obj['spec']['selector']['color']

    def other_env(self):
        current = self.active_env()
        return 'green' if current == 'blue' else 'blue' if current == 'green' else None

    def deploy(self, tag):
        color = self.other_env() or 'blue'
        self.apply('deployment', self.deployment_config, tag=tag, color=color)

        return color

    @log('Waiting for service {name} to become available')
    def wait_for_service(self, name, max_attempts=60):
        attempts = 0
        ip_address = None

        while not ip_address and attempts < max_attempts:
            output('.', '')
            service = self.kube_api.service(self.smoke_service_name)

            try:
                ip_address = (service or {}).obj['status']['loadBalancer']['ingress'][0]['ip']
            except KeyError:
                attempts += 1
                sleep(1)

        if ip_address:
            output('\nService {} is up at {}'.format(name, ip_address))
            return ip_address

        raise ActionFailedError('Timed out while waiting for service {} after {} attempts'.format(name, max_attempts))

    @log('Running smoke tests on {color} deployment...')
    def smoke_test(self, color):
        if self.smoke_service_config:
            self.apply('smoke service', self.smoke_service_config, color=color)
            service_external_ip = self.wait_for_service(self.smoke_service_name)

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

        self.migrate(next_tag)
        next_color = self.deploy(next_tag)

        health_ok = self.smoke_test(next_color)
        if health_ok:
            self.swap(next_color)
        else:
            raise ActionFailedError('Cannot promote {} deployment because smoke tests failed'.format(next_color))

        output('Done!')

    @log('Rolling back to previous deployment...')
    def rollback(self):
        color = self.other_env()

        if color:
            self.swap(color)
        else:
            raise ActionFailedError('Cannot rollback to a previous environment because one does not exist.')

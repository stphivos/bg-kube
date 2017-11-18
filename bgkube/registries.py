from bgkube import cmd
from bgkube.run import Runner
from bgkube.utils import module_type_subclasses


class ContainerRegistry:
    name = None

    def push(self, image):
        raise NotImplementedError()

    def __repr__(self):
        return self.name


class GoogleContainerRegistry(ContainerRegistry):
    alias = 'gcr'
    name = 'Google container registry'

    def __init__(self, runner, cluster_name, cluster_zone, **_):
        self.runner = Runner(
            cmd.GCLOUD_CONTAINER_CLUSTER_GET_CREDENTIALS.format(cluster=cluster_name, zone=cluster_zone),
            runner=runner
        )

    def push(self, image):
        self.runner.start(cmd.GCLOUD_DOCKER_PUSH.format(image))


class AwsContainerRegistry(ContainerRegistry):
    alias = 'ecr'
    name = 'Amazon EC2 Container Registry'

    def __init__(self, runner, cluster_name, cluster_zone, kops_state_store, **_):
        self.runner = Runner(
            cmd.AWS_ECR_GET_CREDENTIALS.format(region=cluster_zone),
            cmd.AWS_KOPS_EXPORT_CONFIG.format(cluster=cluster_name, store=kops_state_store),
            runner=runner
        )

    def push(self, image):
        self.runner.start(cmd.AWS_DOCKER_PUSH.format(image))


DEFAULT = 'gcr'
MODULE = __name__
BUILTIN = {cls.alias: '{}.{}'.format(MODULE, name) for name, cls in module_type_subclasses(MODULE, ContainerRegistry)}


def load(runner, options):
    kwargs = options if isinstance(options, dict) else vars(options)
    container_registry = kwargs.get('container_registry', None)

    if container_registry in BUILTIN or not container_registry:
        selected_registry = BUILTIN[container_registry or DEFAULT]
    else:
        selected_registry = container_registry

    module_name, class_name = '.'.join(selected_registry.split('.')[:-1]), selected_registry.split('.')[-1]
    reg = [cls for name, cls in module_type_subclasses(module_name, ContainerRegistry) if name == class_name][0]

    return reg(runner, **kwargs)

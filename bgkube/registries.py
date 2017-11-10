from bgkube import cmd
from bgkube.run import Runner


class ContainerRegistry:
    name = None

    def __init__(self, runner, cluster_name, cluster_zone):
        self.runner = Runner(cmd.GCLOUD_CONTAINER_CLUSTER_GET_CREDENTIALS.format(
            cluster=cluster_name,
            zone=cluster_zone
        ), runner=runner)

    def push(self, image):
        raise NotImplementedError()

    def __repr__(self):
        return self.name


class GoogleContainerRegistry(ContainerRegistry):
    name = 'Google container registry'

    def push(self, image):
        self.runner.start(cmd.GCLOUD_DOCKER_PUSH.format(image))

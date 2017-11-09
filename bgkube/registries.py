from bgkube.run import Runner


class ContainerRegistry:
    name = None

    def __init__(self, runner, cluster_name, cluster_zone):
        self.runner = Runner('gcloud container clusters get-credentials {cluster} --zone {zone}'.format(
            cluster=cluster_name,
            zone=cluster_zone
        ), runner=runner)

    def __repr__(self):
        return self.name


class GoogleContainerRegistry(ContainerRegistry):
    name = 'Google container registry'

    def push(self, image):
        self.runner.start('gcloud docker -- push {}'.format(image))

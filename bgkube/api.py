import pykube
from yaml import load
from os.path import expanduser

from bgkube.utils import dot_env_dict, read_with_merge_vars


class KubeApi:
    def __init__(self):
        self._client = None

    def client(self):
        if not self._client:
            self._client = pykube.HTTPClient(pykube.KubeConfig.from_file(expanduser('~/.kube/config')))
        return self._client

    def get_config_with_vars(self, config_file, env_file, **attrs):
        merge_vars = dict(dot_env_dict(env_file)) if env_file else {}
        merge_vars.update(attrs)

        for section in read_with_merge_vars(config_file, merge_vars).split('---'):
            yield load(section)

    def apply(self, config_file, env_file, **attrs):
        def apply_object(config):
            obj = getattr(pykube, config['kind'])(self.client(), config)

            if obj.exists():
                obj.update()
            else:
                obj.create()

            return obj.name

        objects = [apply_object(config) for config in self.get_config_with_vars(config_file, env_file, **attrs)]
        return objects

    def resource_by_name(self, resource, name):
        try:
            return getattr(pykube, resource).objects(self.client()).get_by_name(name)
        except pykube.ObjectDoesNotExist:
            return None

    def pods(self, **labels):
        return list(pykube.Pod.objects(self.client()).filter(selector=labels))

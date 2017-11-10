import pykube
from yaml import load
from os.path import expanduser

from bgkube.utils import dot_env_dict, read_with_merge_vars


class KubeApi:
    def __init__(self):
        self.client = pykube.HTTPClient(pykube.KubeConfig.from_file(expanduser('~/.kube/config')))

    def get_config_with_vars(self, config_file, env_file, **attrs):
        merge_vars = dict(dot_env_dict(env_file)) if env_file else {}
        merge_vars.update(attrs)

        data = load(read_with_merge_vars(config_file, merge_vars))
        return data

    def apply(self, config_file, env_file, **attrs):
        config_data = self.get_config_with_vars(config_file, env_file, **attrs)
        obj = getattr(pykube, config_data['kind'])(self.client, config_data)

        if obj.exists():
            obj.update()
        else:
            obj.create()

    def service(self, name):
        try:
            return pykube.Service.objects(self.client).get_by_name(name)
        except pykube.ObjectDoesNotExist:
            return None

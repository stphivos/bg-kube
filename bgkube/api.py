import pykube
from yaml import load
from os.path import expanduser

from bgkube.utils import read_vars, replace_vars


class KubeApi:
    def __init__(self):
        self.client = pykube.HTTPClient(pykube.KubeConfig.from_file(expanduser('~/.kube/config')))

    def config_dict(self, config_file, env_file, **merge_vars):
        values = dict(read_vars(env_file)) if env_file else {}
        values.update(merge_vars)

        with open(config_file) as fs:
            data = load(replace_vars(fs.read(), values))

            return data

    def apply(self, config_file, env_file, **merge_vars):
        data = self.config_dict(config_file, env_file, **merge_vars)
        obj = getattr(pykube, data['kind'])(self.client, data)

        if obj.exists():
            obj.update()
        else:
            obj.create()

    def service(self, name):
        try:
            return pykube.Service.objects(self.client).get_by_name(name)
        except pykube.ObjectDoesNotExist:
            return None

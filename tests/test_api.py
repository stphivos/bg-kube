from mock import patch, Mock
from pykube import ObjectDoesNotExist
from unittest import TestCase
from yaml import load

from bgkube.api import KubeApi


class TestApi(TestCase):
    def setUp(self):
        self.api = KubeApi()
        setattr(self.api, 'client', Mock())

    @patch('bgkube.api.dot_env_dict')
    @patch('bgkube.api.read_with_merge_vars')
    def test_api_get_config_with_vars_returns_config_data_dict_with_merged_vars(self, merge_conf_mock, read_env_mock):
        user_env_vars = {
            'database': 'db-name',
            'port': 5432
        }
        bg_dynamic_vars = {
            'color': 'blue',
            'tag': 123
        }
        merge_vars = dict(user_env_vars, **bg_dynamic_vars)

        read_env_mock.return_value = user_env_vars
        merge_conf_mock.return_value = '''
        metadata:
            labels:
                color: {color}
        spec:
            image: name:{tag}
        env:
            database: {database}
            port: {port}
        '''.format(**merge_vars)

        config = 'config file'
        dot_env = '.env file'
        result = self.api.get_config_with_vars(config, dot_env, **bg_dynamic_vars)

        self.assertEqual(list(result), [load(merge_conf_mock.return_value)])

        read_env_mock.assert_called_once_with(dot_env)
        merge_conf_mock.assert_called_once_with(config, merge_vars)

    @patch('pykube.Deployment.update')
    @patch('pykube.Deployment.exists')
    @patch('bgkube.api.KubeApi.get_config_with_vars')
    def test_api_apply_updates_existing_deployment_using_config_data(self, get_config_mock, exists_mock, update_mock):
        get_config_mock.return_value = iter([{'kind': 'Deployment'}])
        exists_mock.return_value = True

        self.api.apply('config file', '.env file')

        update_mock.assert_called_once_with()

    @patch('pykube.Service.update')
    @patch('pykube.Service.exists')
    @patch('bgkube.api.KubeApi.get_config_with_vars')
    def test_api_apply_updates_existing_service_using_config_data(self, get_config_mock, exists_mock, update_mock):
        get_config_mock.return_value = iter([{'kind': 'Service'}])
        exists_mock.return_value = True

        self.api.apply('config file', '.env file')

        update_mock.assert_called_once_with()

    @patch('pykube.Job.create')
    @patch('pykube.Job.exists')
    @patch('bgkube.api.KubeApi.get_config_with_vars')
    def test_api_apply_creates_new_job_using_config_data(self, get_config_mock, exists_mock, create_mock):
        get_config_mock.return_value = iter([{'kind': 'Job'}])
        exists_mock.return_value = False

        self.api.apply('config file', '.env file')

        create_mock.assert_called_once_with()

    @patch('pykube.Service.objects')
    def test_api_service_returns_service_object_by_name_when_it_exists(self, objects_mock):
        name = 'service name'
        obj = {'name': name}

        get_mock = Mock(return_value=obj)
        objects_mock.return_value = Mock(get_by_name=get_mock)

        result = self.api.service(name)

        self.assertEqual(result, obj)
        get_mock.assert_called_once_with(name)

    @patch('pykube.Service.objects')
    def test_api_service_returns_none_when_not_found_by_name(self, objects_mock):
        objects_mock.return_value = Mock(get_by_name=Mock(side_effect=ObjectDoesNotExist()))

        self.assertIsNone(self.api.service('service name'))

from mock import patch
from unittest import TestCase

from bgkube import cmd
from bgkube.bg import BgKube
from bgkube.errors import ActionFailedError
from tests.__mocks__ import patch_object, get_options, get_random_int, get_random_str


class TestBgKube(TestCase):
    def setUp(self):
        self.options = get_options()
        self.bgkube = BgKube(self.options)

    def test_bgkube_load_options_sets_options_to_class_attributes(self):
        for key in BgKube.required:
            self.assertEqual(getattr(self.bgkube, key), getattr(self.options, key))

    @patch('bgkube.bg.timestamp')
    @patch('bgkube.run.Runner.start')
    def test_bgkube_build_calls_container_build_command_with_expected_attributes(self, start_mock, ts_mock):
        ts_mock.return_value = get_random_int()

        bg = self.bgkube
        bg.build()

        start_mock.assert_called_once_with(cmd.DOCKER_BUILD.format(
            context=bg.context,
            dockerfile=bg.dockerfile,
            image=bg.image_name,
            tag=ts_mock.return_value,
        ))

    def test_bgkube_push_calls_container_registry_push_with_expected_attributes(self):
        bg = self.bgkube

        with patch_object(bg.container_registry, 'push') as push_mock:
            tag = get_random_int()
            bg.push(tag)

            push_mock.assert_called_once_with('{}:{}'.format(bg.image_name, tag))

    @patch('bgkube.api.KubeApi.apply')
    def test_bgkube_apply_calls_kube_api_apply_with_expected_attributes(self, apply_mock):
        filename = get_random_str()
        tag = get_random_int()
        color = get_random_str()

        bg = self.bgkube
        bg.apply('object description', filename, tag, color)

        apply_mock.assert_called_once_with(
            filename,
            bg.env_file,
            TAG=tag,
            COLOR=color
        )

    @patch('bgkube.bg.BgKube.apply')
    def test_bgkube_migrate_does_not_call_apply_when_no_migration_config_provided(self, apply_mock):
        bg = self.bgkube
        bg.db_migration_job_config = None

        bg.migrate(get_random_int())
        apply_mock.assert_not_called()

    @patch('bgkube.bg.BgKube.apply')
    def test_bgkube_migrate_calls_apply_when_migration_config_was_provided(self, apply_mock):
        bg = self.bgkube

        tag = get_random_int()
        bg.migrate(tag)

        apply_mock.assert_called_once_with('db migration', bg.db_migration_job_config, tag=tag)

    @patch('bgkube.bg.BgKube.build')
    @patch('bgkube.bg.BgKube.push')
    @patch('bgkube.bg.BgKube.migrate')
    @patch('bgkube.bg.BgKube.deploy')
    @patch('bgkube.bg.BgKube.smoke_test')
    @patch('bgkube.bg.BgKube.swap')
    def test_bgkube_publish_swaps_to_newly_deployed_env_when_smoke_tests_pass(
            self, swap_mock, smoke_mock, deploy_mock, migrate_mock, push_mock, build_mock):
        new_tag = get_random_int()
        new_color = get_random_str()

        build_mock.return_value = new_tag
        deploy_mock.return_value = new_color
        smoke_mock.return_value = True

        self.bgkube.publish()

        push_mock.assert_called_once_with(new_tag)
        migrate_mock.assert_called_once_with(new_tag)
        smoke_mock.assert_called_once_with(new_color)
        swap_mock.assert_called_once_with(new_color)

    @patch('bgkube.bg.BgKube.build')
    @patch('bgkube.bg.BgKube.push')
    @patch('bgkube.bg.BgKube.migrate')
    @patch('bgkube.bg.BgKube.deploy')
    @patch('bgkube.bg.BgKube.smoke_test')
    @patch('bgkube.bg.BgKube.swap')
    def test_bgkube_publish_does_not_swap_to_newly_deployed_env_when_smoke_tests_fail(
            self, swap_mock, smoke_mock, deploy_mock, migrate_mock, push_mock, build_mock):
        build_mock.return_value = get_random_int()
        deploy_mock.return_value = get_random_str()
        smoke_mock.return_value = False

        self.assertRaises(ActionFailedError, self.bgkube.publish)

        swap_mock.assert_not_called()

    @patch('bgkube.bg.BgKube.swap')
    @patch('bgkube.bg.BgKube.other_env')
    def test_bgkube_rollback_swaps_service_to_other_env_when_it_exists(self, other_env_mock, swap_mock):
        other_env_mock.return_value = 'green'

        self.bgkube.rollback()

        swap_mock.assert_called_once_with(other_env_mock.return_value)

    @patch('bgkube.bg.BgKube.swap')
    @patch('bgkube.bg.BgKube.other_env')
    def test_bgkube_rollback_does_not_swap_to_other_env_when_it_does_not_exist(self, other_env_mock, swap_mock):
        other_env_mock.return_value = None

        self.assertRaises(ActionFailedError, self.bgkube.rollback)

        swap_mock.assert_not_called()

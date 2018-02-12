from mock import patch, Mock
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

        with patch_object(bg.registry, 'push') as push_mock:
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
            COLOR=color,
            ENV_FILE=bg.env_file
        )

    @patch('bgkube.api.KubeApi.pods')
    @patch('bgkube.run.Runner.start')
    def test_bgkube_pod_exec_runs_command_on_any_ready_pod_from_kube_api_and_returns_stdout(self, start_mock, pod_mock):
        pod = Mock(ready=False, name='pod1')
        ready_pod = Mock(ready=True, name='pod2')
        pod_mock.return_value = [pod, ready_pod]
        start_mock.return_value = get_random_str()

        tag, command, arg1, arg2 = get_random_int(), 'echo', '"hello"', '"world'
        stdout = self.bgkube.pod_exec(tag, command, arg1, arg2)
        self.assertEqual(stdout, start_mock.return_value)

        pod_mock.assert_called_once_with(tag=tag)
        start_mock.assert_called_once_with(
            cmd.KUBECTL_EXEC.format(pod=ready_pod.name, command=command, args=' '.join([arg1, arg2])),
            capture=True
        )

    @patch('bgkube.bg.BgKube.apply')
    def test_bgkube_migrate_initial_does_not_call_apply_when_no_migrations_config_seed_provided(self, apply_mock):
        bg = self.bgkube
        bg.db_migrations_job_config_seed = None

        bg.migrate_initial(get_random_int())
        apply_mock.assert_not_called()

    @patch('bgkube.bg.BgKube.apply')
    def test_bgkube_migrate_initial_calls_apply_when_migrations_config_seed_was_provided(self, apply_mock):
        bg = self.bgkube

        tag = get_random_int()
        bg.migrate_initial(tag)

        apply_mock.assert_called_once_with('db migration', bg.db_migrations_job_config_seed, tag=tag)

    @patch('bgkube.bg.BgKube.pod_exec')
    def test_bgkube_migrate_apply_executes_db_migrations_apply_command_when_supplied(self, exec_mock):
        tag = get_random_int()

        self.bgkube.db_migrations_apply_command = get_random_str()
        self.bgkube.migrate_apply(tag)

        exec_mock.assert_called_once_with(tag, self.bgkube.db_migrations_apply_command)

    @patch('bgkube.bg.BgKube.pod_exec')
    def test_bgkube_migrate_apply_returns_stdout_from_db_migrations_status_command_when_supplied(self, exec_mock):
        tag = get_random_int()
        exec_mock.return_value = get_random_str()

        self.bgkube.db_migrations_status_command = get_random_str()
        stdout = self.bgkube.migrate_apply(tag)

        self.assertEqual(stdout, exec_mock.return_value)
        exec_mock.assert_called_once_with(tag, self.bgkube.db_migrations_status_command)

    @patch('bgkube.bg.BgKube.pod_exec')
    def test_bgkube_migrate_apply_returns_null_when_db_migrations_status_command_not_supplied(self, exec_mock):
        tag = get_random_int()

        self.bgkube.db_migrations_status_command = None
        stdout = self.bgkube.migrate_apply(tag)

        self.assertIsNone(stdout)
        exec_mock.assert_not_called()

    @patch('bgkube.bg.BgKube.pod_exec')
    def test_bgkube_migrate_rollback_executes_db_migrations_rollback_command_when_supplied(self, exec_mock):
        tag, prev_state = get_random_int(), get_random_str()

        self.bgkube.db_migrations_rollback_command = get_random_str()
        self.bgkube.migrate_rollback(tag, prev_state)

        exec_mock.assert_called_once_with(tag, self.bgkube.db_migrations_rollback_command, prev_state)

    @patch('bgkube.bg.BgKube.pod_exec')
    def test_bgkube_migrate_rollback_does_not_execute_empty_db_migrations_rollback_command(self, exec_mock):
        tag, prev_state = get_random_int(), get_random_str()

        self.bgkube.db_migrations_rollback_command = None
        self.bgkube.migrate_rollback(tag, prev_state)

        exec_mock.assert_not_called()

    @patch('bgkube.bg.BgKube.active_env')
    @patch('bgkube.bg.BgKube.migrate_apply')
    @patch('bgkube.bg.BgKube.migrate_initial')
    def test_bgkube_migrate_performs_initial_migrations_when_initial_deployment(self, init_mock, apply_mock, env_mock):
        env_mock.return_value = None
        apply_mock.return_value = get_random_str()

        tag = get_random_int()
        is_initial, prev_state = self.bgkube.migrate(tag)

        self.assertEqual(is_initial, True)
        self.assertIsNone(prev_state)

        init_mock.assert_called_once_with(tag)
        apply_mock.assert_not_called()

    @patch('bgkube.bg.BgKube.active_env')
    @patch('bgkube.bg.BgKube.migrate_apply')
    @patch('bgkube.bg.BgKube.migrate_initial')
    def test_bgkube_migrate_applies_latest_migrations_when_recurring_deployment(self, init_mock, apply_mock, env_mock):
        env_mock.return_value = get_random_str()
        apply_mock.return_value = get_random_str()

        tag = get_random_int()
        is_initial, prev_state = self.bgkube.migrate(tag)

        self.assertEqual(is_initial, False)
        self.assertEqual(prev_state, apply_mock.return_value)

        init_mock.assert_not_called()
        apply_mock.assert_called_once_with(tag)

    @patch('bgkube.api.KubeApi.resource_by_name')
    def test_bgkube_active_env_returns_public_service_selector_color_when_found(self, resource_mock):
        service = Mock(obj={'spec': {'selector': {'color': get_random_str()}}})
        resource_mock.return_value = service

        env = self.bgkube.active_env()

        self.assertEqual(env, service.obj['spec']['selector']['color'])
        resource_mock.assert_called_once_with('Service', self.bgkube.service_name)

    @patch('bgkube.api.KubeApi.resource_by_name')
    def test_bgkube_active_env_returns_null_when_public_service_not_found(self, resource_mock):
        resource_mock.return_value = None

        env = self.bgkube.active_env()

        self.assertIsNone(env)
        resource_mock.assert_called_once_with('Service', self.bgkube.service_name)

    @patch('bgkube.bg.BgKube.active_env')
    def test_bgkube_other_env_returns_opposite_of_active_env_otherwise_null(self, active_env_mock):
        active_env_mock.return_value = 'blue'
        self.assertEqual(self.bgkube.other_env(), 'green')

        active_env_mock.return_value = 'green'
        self.assertEqual(self.bgkube.other_env(), 'blue')

        active_env_mock.return_value = None
        self.assertIsNone(self.bgkube.other_env())

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
        is_initial, prev_state = False, None

        build_mock.return_value = new_tag
        deploy_mock.return_value = new_color
        migrate_mock.return_value = is_initial, prev_state
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
        is_initial, prev_state = False, None

        build_mock.return_value = get_random_int()
        deploy_mock.return_value = get_random_str()
        migrate_mock.return_value = is_initial, prev_state
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

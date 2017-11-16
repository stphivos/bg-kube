from unittest import TestCase

from bgkube.run import Runner


class TestRun(TestCase):
    def test_run_get_init_commands_silenced_redirects_to_dev_null_both_parts_joined_with_logical_and(self):
        result = Runner('echo "a" && echo "b"').get_init_commands_silenced()
        self.assertEqual(result, 'echo "a" {0} && echo "b" {0}'.format(Runner.REDIRECTION))

    def test_run_get_init_commands_silenced_redirects_to_dev_null_both_parts_joined_with_logical_or(self):
        result = Runner('echo "a" || echo "b"').get_init_commands_silenced()
        self.assertEqual(result, 'echo "a" {0} || echo "b" {0}'.format(Runner.REDIRECTION))

    def test_run_get_init_commands_silenced_redirects_to_dev_null_all_parts_containing_mixed_logical_operators(self):
        result = Runner('echo "a" || echo "b" && echo "c"').get_init_commands_silenced()
        self.assertEqual(result, 'echo "a" {0} || echo "b" {0} && echo "c" {0}'.format(Runner.REDIRECTION))

    def test_run_get_init_commands_silenced_redirects_to_dev_null_all_commands_with_mixed_logical_operators(self):
        result = Runner(
            'echo "a" || echo "b" && echo "c"',
            'echo "d" && echo "e"',
            'echo "f" || echo "g"',
        ).get_init_commands_silenced()

        self.assertEqual(result, 'echo "a" {0} || echo "b" {0} && echo "c" {0}; '
                                 'echo "d" {0} && echo "e" {0}; '
                                 'echo "f" {0} || echo "g" {0}'.format(Runner.REDIRECTION))

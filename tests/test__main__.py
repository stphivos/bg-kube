from mock import Mock
from unittest import TestCase

from bgkube.__main__ import get_parser
from bgkube.bg import BgKube
from tests.__mocks__ import get_random_str


class TestMain(TestCase):
    def test_main_get_parser_args_match_bgkube_attributes(self):
        args = [arg.dest for arg in get_parser()._actions if arg.dest not in ['help', 'command', 'command_args']]
        options = Mock(**{arg: get_random_str() for arg in args if arg in BgKube.required})
        bg = BgKube(options)

        for name in args:
            self.assertIsNotNone(getattr(bg, name, None), name)

    def test_main_get_parser_args_command_choices_match_bgkube_methods(self):
        command = [arg for arg in get_parser()._actions if arg.dest == 'command'][0]

        for name in command.choices:
            self.assertIsNotNone(getattr(BgKube, name, None), name)

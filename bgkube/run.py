from os import environ
from subprocess import call

from bgkube.errors import ActionFailedError


class Runner:
    def __init__(self, *init_commands, **kwargs):
        self.init_commands = list(init_commands)

        runner = kwargs.get('runner', None)
        if runner:
            self.init_commands.extend(runner.init_commands)

    def user_env(self, env):
        result = environ.copy()
        result.update(**env)

        return result

    def start(self, command, silent=False, **env):
        return_code = call('{}; {}'.format(
            '; '.join(self.init_commands), command),
            env=self.user_env(env),
            shell=True
        )

        if return_code == 0 or silent:
            return return_code
        else:
            raise ActionFailedError('Invocation of command \'{}\' failed with code {}'.format(command, return_code))

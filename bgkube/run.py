from os import environ
from subprocess import Popen, PIPE

from bgkube.errors import ActionFailedError
from bgkube.utils import log


class Runner:
    REDIRECTION = '&> /dev/null'

    def __init__(self, *init_commands, **kwargs):
        self.init_commands = list(init_commands)

        runner = kwargs.get('runner', None)
        if runner:
            self.init_commands = runner.init_commands + self.init_commands

    def user_env(self, env):
        result = environ.copy()
        result.update(**env)

        return result

    def get_init_commands_silenced(self):
        def silence(command):
            return '{} {}'.format(command, self.REDIRECTION) if self.REDIRECTION not in command else command

        for i, _ in enumerate(self.init_commands):
            for separator in [' && ', ' || ']:
                self.init_commands[i] = separator.join(silence(p) for p in self.init_commands[i].split(separator))

        return '; '.join(silence(c) for c in self.init_commands)

    @log('$ {command}')
    def start(self, command, silent=False, capture=False, **env):
        def read(st_result):
            if st_result and isinstance(st_result, bytes):
                st_result = st_result.decode('utf-8').strip()
            return st_result

        target_command = '{}; {}'.format(self.get_init_commands_silenced(), command)
        kwargs = dict() if not capture else dict(stdin=PIPE, stdout=PIPE, stderr=PIPE)

        process = Popen(target_command, env=self.user_env(env), shell=True, **kwargs)
        output, error = process.communicate()
        return_code = process.returncode

        if return_code == 0 or silent:
            return return_code if not capture else read(output)
        else:
            raise ActionFailedError('Command invocation failed with code {}: {}'.format(return_code, read(error)))

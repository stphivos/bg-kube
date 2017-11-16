from __future__ import print_function

import os
import time

from bgkube.errors import RequiredOptionError


def require(obj, attr):
    value = getattr(obj, attr, None)

    if value is None:
        raise RequiredOptionError(attr)

    return value


def dot_env_dict(filename):
    with open(filename) as fp:
        for line in fp.readlines():
            line = line.strip()

            if not line or line.startswith('#') or '=' not in line:
                continue

            k, v = line.split('=', 1)
            k, v = k.strip(), v.strip()

            quotes = ['\'', '"']
            v_unquoted = v.strip(''.join(quotes))

            if v_unquoted.isdigit() and len(v_unquoted) == len(v):
                v = int(v_unquoted)
            else:
                v = v_unquoted

            yield k, v


def read_with_merge_vars(filename, merge_vars):
    with open(filename) as fs:
        result = fs.read()

        for k, v in merge_vars.items():
            result = result.replace('${}'.format(k), str(v))

        return result


def timestamp():
    return int(time.time())


def output(msg, end='\n', **kwargs):
    if not os.environ.get('PYTEST_CURRENT_TEST', None):
        print(msg, end=end, **kwargs)


def log(message, **defaults):
    def wrap(func):
        def wrapped(*args, **kwargs):
            params = {}

            import inspect
            spec = inspect.getargspec(func)

            for i, v in enumerate(spec.args or ()):
                params[v] = args[i] if i < len(args) else kwargs.get(v, '')

            if 'self' in params:
                attrs = {k: v for k, v in params.pop('self').__dict__.items() if k[0].isalpha() and not callable(v)}
                params = dict(attrs, **params)

            for k, v in defaults.items():
                if not params.get(k, ''):
                    params[k] = v

            if message.strip().startswith('$'):
                output(message.format(**{k: '{}'.format(v) for k, v in params.items()}))
            else:
                output('=> ' + message.format(**{k: '\'{}\''.format(v) for k, v in params.items()}))
            result = func(*args, **kwargs)

            return result

        return wrapped

    return wrap

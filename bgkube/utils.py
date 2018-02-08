from __future__ import print_function

import os
import sys
import time
import requests
from inspect import isclass

from bgkube.errors import RequiredOptionError


def require(obj, attr):
    value = getattr(obj, attr, None)

    if value is None:
        raise RequiredOptionError(attr)

    return value


def dot_env_dict(filename):
    # TODO: Handle lines with inline comment
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

        for k in sorted(merge_vars.keys(), reverse=True):
            result = result.replace('${}'.format(k), str(merge_vars[k]))

        return result


def timestamp():
    return int(time.time())


def error(msg, **output_kwargs):
    output(msg, **output_kwargs)
    exit(1)


def output(msg, end='\n', **kwargs):
    if not os.environ.get('PYTEST_CURRENT_TEST', None):
        flush = kwargs.pop('flush', False)
        print(msg, end=end, **kwargs)
        if flush:
            sys.stdout.flush()


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


def module_type_subclasses(mod, t):
    def is_valid(obj):
        return isclass(obj) and issubclass(obj, t) and obj != t

    for name, cls in __import__(mod, fromlist=[mod]).__dict__.items():
        if is_valid(cls):
            yield name, cls


def get_loadbalancer_address(service):
    # TODO: Should be improved to either returning all possible addresses or get smarter at detecting the right one
    ports = service.obj['spec']['ports'][0]
    scheme = ports.get('name', 'http')
    port = ports['port']

    ingress = service.obj['status']['loadBalancer']['ingress'][0]
    host = ingress.get('ip', None) or ingress.get('hostname', None)

    return '{}://{}:{}'.format(scheme, host, port)


def is_host_up(address, status_code=200):
    try:
        response = requests.get(address)
        return response.status_code == status_code
    except requests.exceptions.ConnectionError:
        return False

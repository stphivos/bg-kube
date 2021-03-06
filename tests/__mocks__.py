from random import randint, choice
from string import ascii_letters
from sys import maxsize
from mock import patch

patch_object = patch.object = patch.object


class DictionaryObject(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


def get_random_int(min_value=-maxsize, max_value=maxsize):
    return randint(min_value, max_value)


def get_random_str(min_length=1, max_length=100):
    return ''.join(choice(ascii_letters) for _ in range(randint(min_length, max_length)))


def get_values():
    return dict(
        a=1,
        b='2',
        c='d',
        e='f=g',
        h=' i '
    )


def get_lines(values):
    def value(x):
        if isinstance(x, str) and x.isdigit():
            return '\'{}\''.format(x)
        return x

    return ['{}={}'.format(k, value(v)) for k, v in values.items()]


def get_options():
    return DictionaryObject(
        docker_machine_name='my_rest_api',
        cluster_zone='us-central1-a',
        cluster_name='my-us-cluster',
        image_name='gcr.io/project-id/my-rest-api',
        service_name='svc-rest-api',
        service_config='./config/services/public.yaml',
        deployment_name='dep-rest-api',
        deployment_config='./config/deployments/main.yaml',
        context='.',
        dockerfile='./Dockerfile',
        env_file='.env.prod',
        smoke_service_name='svc-rest-api-e2e',
        smoke_tests_command='pytest -s ./src/e2e',
        smoke_service_config='./config/services/smoke.yaml',
        db_migrations_job_config_seed='./config/jobs/db-migrate.yaml',
        kops_state_store='s3://todoapp-cluster-state-store'
    )


def get_named_resource(kind=None, name=None):
    return {
        'kind': kind or get_random_str(),
        'metadata': {
            'name': name or get_random_str()
        }
    }

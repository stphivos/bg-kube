class DictionaryObject(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


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
        deployment_config='./config/deployments/main.yaml',
        context='.',
        dockerfile='./Dockerfile',
        env_file='.env.prod',
        smoke_service_name='svc-rest-api-e2e',
        smoke_tests_command='pytest -s ./src/e2e',
        smoke_service_config='./config/services/smoke.yaml',
        db_migration_job_config='./config/jobs/db-migrate.yaml',
    )

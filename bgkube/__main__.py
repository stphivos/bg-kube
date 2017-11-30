from argparse import ArgumentParser
from traceback import format_exc

from bgkube.bg import BgKube
from bgkube.errors import BlueGreenError
from bgkube.utils import dot_env_dict, error


def get_parser():
    parser = ArgumentParser()
    parser.add_argument('command', help='', default='publish', choices=['publish', 'rollback', 'build', 'push'])
    parser.add_argument('command_args', nargs='*')
    parser.add_argument('-e', '--env-file', help='.env file for the options below and application vars in the configs')
    parser.add_argument('-c', '--cluster-name', help='unique name of the cluster')
    parser.add_argument('-z', '--cluster-zone', help='zone name of the cluster location')
    parser.add_argument('-m', '--docker-machine-name', help='name of the docker machine if applicable')
    parser.add_argument('-i', '--image-name', help='name of the container image to build using docker')
    parser.add_argument('-s', '--service-name', help='name of the main service intended to serve clients')
    parser.add_argument('--service-config', help='config of the main service')
    parser.add_argument('--service-timeout', help='timeout secs to wait for healthy state or return an error')
    parser.add_argument('--deployment-config', help='config of the deployment containing the main service pods')
    parser.add_argument('--deployment-timeout', help='timeout secs to wait for healthy state or return an error')
    parser.add_argument('-x', '--context', help='docker context path used to build the container image')
    parser.add_argument('-d', '--dockerfile', help='Dockerfile path')
    parser.add_argument('--smoke-service-config', help='config of the smoke service lb exposed for health checks')
    parser.add_argument('--smoke-tests-command', help='shell command to run health checks against the smoke service')
    parser.add_argument('--db-migrations-job-config-seed', help='job config to populate the database with initial data')
    parser.add_argument('--db-migrations-job-timeout', help='timeout secs to wait for healthy state or return an error')
    parser.add_argument(
        '--db-migrations-status-command',
        help='shell command executed on any of the running deployment pods to return the current migrations status'
    )
    parser.add_argument(
        '--db-migrations-apply-command',
        help='shell command executed on any of the running deployment pods to apply the latest migrations generated in '
             'the current image'
    )
    parser.add_argument(
        '--db-migrations-rollback-command',
        help='shell command executed on any of the running deployment pods with the migrations status command stdout '
             'as argument - retrieved before applying migrations, to perform a rollback to that state'
    )
    parser.add_argument('--kops-state-store', help='aws cluster state storage bucket name')
    parser.add_argument('--container-registry', help='container registry alias or implementation class')

    return parser


def load_options_from_env(options):
    for k, v in dict(dot_env_dict(options.env_file)).items():
        attr_name = k.lower()

        if hasattr(options, attr_name) and getattr(options, attr_name) is None:
            setattr(options, attr_name, v)


def run():
    parser = get_parser()
    options = parser.parse_args()

    if options.env_file:
        load_options_from_env(options)

    try:
        getattr(BgKube(options), options.command)(*options.command_args)
    except BlueGreenError as e:
        error(e)
    except Exception:
        error(format_exc())


if __name__ == '__main__':
    run()

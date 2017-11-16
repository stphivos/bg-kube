from argparse import ArgumentParser

from bgkube.bg import BgKube
from bgkube.utils import dot_env_dict, output


def get_parser():
    parser = ArgumentParser()
    parser.add_argument('command', help='', default='publish', choices=['publish', 'rollback'])
    parser.add_argument('-e', '--env-file', help='.env file for the options below and application vars in the configs')
    parser.add_argument('-c', '--cluster-name', help='unique name of the cluster')
    parser.add_argument('-z', '--cluster-zone', help='zone name of the cluster location')
    parser.add_argument('-m', '--docker-machine-name', help='name of the docker machine if applicable')
    parser.add_argument('-i', '--image-name', help='name of the container image to build using docker')
    parser.add_argument('-s', '--service-name', help='name of the public service intended to be exposed')
    parser.add_argument('--service-config', help='public service config')
    parser.add_argument('--deployment-name', help='name of the deployment containing the public service pods')
    parser.add_argument('--deployment-config', help='deployment config')
    parser.add_argument('-x', '--context', help='docker context path used to build the container image')
    parser.add_argument('-d', '--dockerfile', help='Dockerfile path')
    parser.add_argument('--smoke-service-name', help='name of the smoke service meant to be exposed for health checks')
    parser.add_argument('--smoke-service-config', help='smoke service config')
    parser.add_argument('--smoke-tests-command', help='shell command to run health checks against the smoke service')
    parser.add_argument('--db-migrations-job-config-seed', help='job config to populate the database with initial data')
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
        getattr(BgKube(options), options.command)()
    except Exception as e:
        output(e)


if __name__ == '__main__':
    run()

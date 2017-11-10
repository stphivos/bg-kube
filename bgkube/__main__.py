from argparse import ArgumentParser

from bgkube.bg import BgKube
from bgkube.utils import read_vars, output


def run():
    parser = ArgumentParser()
    parser.add_argument('command', help='', default='publish', choices=['publish', 'rollback'])
    parser.add_argument('-e', '--env-file', help='.env file for options below and application vars in the configs')
    parser.add_argument('-c', '--cluster-name', help='unique name of the cluster')
    parser.add_argument('-z', '--cluster-zone', help='zone name of the cluster location of the cluster')
    parser.add_argument('-m', '--docker-machine-name', help='name of docker machine')
    parser.add_argument('-i', '--image-name', help='name of container image to build using docker')
    parser.add_argument('-s', '--service-name', help='name of the public service intended to be exposed')
    parser.add_argument('--service-config', help='public service config')
    parser.add_argument('--deployment-config', help='deployment config containing the public service pods')
    parser.add_argument('-x', '--context', help='docker context path used to build the container image')
    parser.add_argument('-d', '--dockerfile', help='Dockerfile path')
    parser.add_argument('--smoke-service-name', help='name of the smoke service meant to be exposed for health checks')
    parser.add_argument('--smoke-service-config', help='smoke service config')
    parser.add_argument('--smoke-tests-command', help='shell command to run health checks against the smoke service')
    parser.add_argument('--db-migration-job-config', help='job config to sync the database based on the latest image')

    options = parser.parse_args()
    if options.env_file:
        for k, v in dict(read_vars(options.env_file)).items():
            attr_name = k.lower()

            if hasattr(options, attr_name) and getattr(options, attr_name) is None:
                setattr(options, attr_name, v)

    try:
        getattr(BgKube(options), options.command)()
    except Exception as e:
        output(e)


if __name__ == '__main__':
    run()

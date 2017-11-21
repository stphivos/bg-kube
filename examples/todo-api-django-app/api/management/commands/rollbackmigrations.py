from __future__ import print_function

from django.core.management import BaseCommand

from . import run


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app_migrations', nargs='*')

    def handle(self, *_, **options):
        for app_migrations in options['app_migrations']:
            app, migration = app_migrations.split(':')

            print(run('migrate {} {}'.format(app, migration)))

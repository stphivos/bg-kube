from __future__ import print_function

from django.core.management import BaseCommand

from . import run


class Command(BaseCommand):
    def handle(self, *_, **__):
        app_migrations = []
        apps = run('showmigrations | grep -vE "\[(X| )\]"').split('\n')

        for app in apps:
            applied = run('showmigrations {} | grep -E "\[X\]"'.format(app))

            if applied:
                last = [m.replace('[X]', '').strip() for m in applied.split('\n')][-1]
                app_migrations.append('{}:{}'.format(app, last))

        print(' '.join(app_migrations))

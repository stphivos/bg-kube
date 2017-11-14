import os
from dotenv import load_dotenv, find_dotenv


def load_env():
    env = os.environ.get('ENV', 'dev')
    load_dotenv(find_dotenv('.env.{}'.format(env)))

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')

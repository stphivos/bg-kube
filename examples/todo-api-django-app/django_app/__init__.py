import os
from dotenv import load_dotenv, find_dotenv


def load_env():
    load_dotenv(find_dotenv(os.environ.get('ENV_FILE', '.env.dev')))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_app.settings')

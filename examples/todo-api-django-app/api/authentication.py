from django.contrib.auth.models import User
from os import environ
from requests import get
from rest_framework.authentication import BaseAuthentication


class UserApiAuthentication(BaseAuthentication):
    def discover_user_api(self):
        service = environ['SERVICE_USER_API_NAME']
        port = environ['{}_SERVICE_PORT'.format(service.upper().replace('-', '_'))]

        return 'http://{service}.{namespace}.svc.cluster.local:{port}'.format(
            service=service,
            namespace=environ['SERVICE_USER_API_NAMESPACE'],
            port=port
        )

    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[-1]

        if token:
            headers = dict(Authorization='Bearer {}'.format(token))
            data = get('{}/user/'.format(self.discover_user_api()), headers=headers).json()

            if data.get('username', None):
                _ = data.pop('uuid')
                user = (User.objects.filter(username=data['username'])[:1] or [User.objects.create_user(**data)])[0]

                return user, None

        return None

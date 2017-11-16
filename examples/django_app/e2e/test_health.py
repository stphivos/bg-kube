import os
import requests
from unittest import TestCase


class SmokeTests(TestCase):
    """ You should off course write better health checks than the following... """

    def test_service_is_up(self):
        response = requests.get('http://{}/todos/'.format(os.environ['TEST_HOST']))
        assert response.status_code == 200, response.status_code

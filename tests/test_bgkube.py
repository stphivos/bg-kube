from unittest import TestCase

from bgkube.bg import BgKube
from tests.__mocks__ import get_options


class TestBgKube(TestCase):
    def test_bgkube_loads_options_as_attributes(self):
        options = get_options()
        bg = BgKube(options)

        for key in BgKube.required:
            self.assertEqual(getattr(bg, key), getattr(options, key))

from unittest import TestCase

from bgkube.registries import load, GoogleContainerRegistry, AwsContainerRegistry
from tests.__mocks__ import get_options


class TestRegistries(TestCase):
    def test_registries_gcr_by_alias(self):
        opt = get_options()
        opt.container_registry = GoogleContainerRegistry.alias

        obj = load(None, opt)
        self.assertIsInstance(obj, GoogleContainerRegistry)

    def test_registries_gcr_by_qualified_class_name(self):
        opt = get_options()
        opt.container_registry = '{}.{}'.format(GoogleContainerRegistry.__module__, GoogleContainerRegistry.__name__)

        obj = load(None, opt)
        self.assertIsInstance(obj, GoogleContainerRegistry)

    def test_registries_ecr_by_alias(self):
        opt = get_options()
        opt.container_registry = AwsContainerRegistry.alias

        obj = load(None, opt)
        self.assertIsInstance(obj, AwsContainerRegistry)

    def test_registries_ecr_by_qualified_class_name(self):
        opt = get_options()
        opt.container_registry = '{}.{}'.format(AwsContainerRegistry.__module__, AwsContainerRegistry.__name__)

        obj = load(None, opt)
        self.assertIsInstance(obj, AwsContainerRegistry)

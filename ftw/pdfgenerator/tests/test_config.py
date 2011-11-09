"""Unit tests testing the default configuration utility.
"""

from ftw.pdfgenerator.config import DefaultConfig
from ftw.pdfgenerator.interfaces import IConfig
from unittest2 import TestCase
from zope.interface.verify import verifyClass
import os


class TestDefaultConfigurationUtility(TestCase):

    def test_config_implements_interface(self):
        self.assertTrue(IConfig.implementedBy(DefaultConfig))
        verifyClass(IConfig, DefaultConfig)

    def test_remove_build_directory_true_by_default(self):
        self.assertTrue(DefaultConfig().remove_build_directory)

    def test_build_directory_existing(self):
        path = DefaultConfig().get_build_directory()
        self.assertTrue(os.path.exists(path))
        os.rmdir(path)

    def test_build_directory_is_writeable(self):
        path = DefaultConfig().get_build_directory()
        self.assertTrue(os.access(path, os.R_OK | os.W_OK))
        os.rmdir(path)

    def test_build_directory_not_the_same_twice(self):
        config = DefaultConfig()
        path_one = config.get_build_directory()
        path_two = config.get_build_directory()

        self.assertNotEqual(path_one, path_two)
        os.rmdir(path_one)
        os.rmdir(path_two)

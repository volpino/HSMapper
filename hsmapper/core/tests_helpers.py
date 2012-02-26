"""
Helpers for hsmapper tests
"""

from django.utils import unittest
from django.test.client import Client


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

"""
Tests for hsmapper.core app
"""

from hsmapper.core.tests_helpers import BaseTestCase


class SimpleTest(BaseTestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

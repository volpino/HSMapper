"""
Tests for hsmapper.core app
"""

from BeautifulSoup import BeautifulSoup
import json

from hsmapper.core.tests_helpers import BaseTestCase


class NavigationTest(BaseTestCase):
    def test_logged_user(self):
        with self.login("admin", "pass"):
            response = self.get("index")
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Logged in as admin" in response.content)
            self.assertTrue("globals.username = " in response.content)

    def test_not_logged_user(self):
        response = self.get("index")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Logged in as" not in response.content)
        self.assertTrue("globals.username = " not in response.content)


class ApiTest(BaseTestCase):
    def test_get_hospitals(self):
        response = self.get("api-get-hospitals")
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.content)
        self.assertEqual(len(json_data["features"]), 15)
        feature = json_data["features"][0]
        for attr in ["geometry", "id", "properties"]:
            self.assertTrue(attr in feature)

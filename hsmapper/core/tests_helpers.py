"""
Helpers for hsmapper tests
"""

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse


class BaseTestCase(TestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        self.client = Client()

    def get(self, url_name, *args, **kwargs):
        return self.client.get(reverse(url_name, args=args, kwargs=kwargs))

    def post(self, url_name, *args, **kwargs):
        data = kwargs.pop("data", None)
        return self.client.post(
            reverse(url_name, args=args, kwargs=kwargs),
            data
        )

    def login(self, user, password):
        return Login(self, user, password)


class Login(object):
    def __init__(self, testcase, user, password):
        self.testcase = testcase
        success = testcase.client.login(username=user, password=password)
        self.testcase.assertTrue(
            success,
            "login with username=%r, password=%r failed" % (user, password)
        )

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.testcase.client.logout()

"""
Helpers for hsmapper tests
"""

from urllib import urlencode

from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse


class BaseTestCase(TestCase):
    fixtures = ["test_data.json"]

    def setUp(self):
        self.client = Client()

    def get(self, url_name, *args, **kwargs):
        param = kwargs.pop("param", None)
        if param:
            url = "%s?%s" % (reverse(url_name, args=args, kwargs=kwargs),
                             urlencode(param))
        else:
            url = reverse(url_name, args=args, kwargs=kwargs)
        return self.client.get(url)

    def post(self, url_name, *args, **kwargs):
        data = kwargs.pop("data", {})
        url = reverse(url_name, args=args, kwargs=kwargs)
        return self.client.post(url, data)

    def login(self, user, password):
        return Login(self, user, password)

    def superuser_login(self):
        return Login(self, "admin", "pass")


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

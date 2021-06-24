"""Subclasses Django test client to allow for easy login"""

from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.http import HttpRequest
from django.test import TestCase
from django.test.client import Client

User = get_user_model()


class TestClient(Client):
    """
    Allows for 'fake logins' of a user so we don't need to expose a 'login' HTTP endpoint
    """
    def login_user(self, user):
        """
        Login as specified user, does not depend on auth backend (hopefully)

        This is based on Client.login() with a small hack that does not
        require the call to authenticate()
        """
        user.backend = "django.contrib.auth.backends.ModelBackend"
        engine = import_module(settings.SESSION_ENGINE)

        # Create a fake request to store login details.
        request = HttpRequest()

        request.session = engine.SessionStore()
        login(request, user)

        # Set the cookie to represent the session.
        session_cookie = settings.SESSION_COOKIE_NAME
        self.cookies[session_cookie] = request.session.session_key
        cookie_data = {
            'max-age': None,
            'path': '/',
            'domain': settings.SESSION_COOKIE_DOMAIN,
            'secure': settings.SESSION_COOKIE_SECURE or None,
            'expires': None,
        }
        self.cookies[session_cookie].update(cookie_data)

        # Save the session values.
        request.session.save()


class LoggedInTestCase(TestCase):
    """
    All tests for the views.py
    """

    def setUp(self):
        """
        Setup for tests
        """
        super().setUp()
        self.client = TestClient()
        self.user = User(username='tester', email='tester@test.com')
        self.user.save()
        self.client.login_user(self.user)

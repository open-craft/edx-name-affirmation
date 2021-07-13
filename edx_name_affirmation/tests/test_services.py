"""
Tests for NameAffirmation services
"""

import types

from django.contrib.auth import get_user_model
from django.test import TestCase

from edx_name_affirmation import api as edx_name_affirmation_api
from edx_name_affirmation.services import NameAffirmationService

User = get_user_model()


class NameAffirmationServiceTest(TestCase):
    """
    Tests for NameAffirmationService
    """
    def test_basic(self):
        """
        See if the NameAffirmationService exposes the expected methods
        """

        service = NameAffirmationService()

        for attr_name in dir(edx_name_affirmation_api):
            attr = getattr(edx_name_affirmation_api, attr_name, None)
            if isinstance(attr, types.FunctionType):
                self.assertTrue(hasattr(service, attr_name))

    def test_singleton(self):
        """
        Test to make sure the NameAffirmationService is a singleton.
        """
        service1 = NameAffirmationService()
        service2 = NameAffirmationService()
        self.assertIs(service1, service2)

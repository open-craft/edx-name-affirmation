"""
Tests for toggles.py
"""
from edx_toggles.toggles.testutils import override_waffle_flag

from django.test import TestCase

from edx_name_affirmation.toggles import VERIFIED_NAME_FLAG, is_verified_name_enabled


class TestNameAffirmationToggles(TestCase):
    """
    Test for toggles.py
    """
    def test_verified_name_flag_false(self):
        self.assertFalse(is_verified_name_enabled())

    @override_waffle_flag(VERIFIED_NAME_FLAG, True)
    def test_verified_name_flag_true(self):
        self.assertTrue(is_verified_name_enabled())

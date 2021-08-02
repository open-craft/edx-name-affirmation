"""
Unit tests for the NameAffirmation admin classes
"""


from unittest import mock

from django.contrib.admin.sites import AdminSite
from django.test import TestCase

from edx_name_affirmation.admin import VerifiedNameAdmin, VerifiedNameConfigAdmin
from edx_name_affirmation.models import VerifiedName, VerifiedNameConfig


class NameAffirmationAdminTests(TestCase):
    """
    Unit tests for the NameAffirmation admin classes
    """

    def setUp(self):
        super().setUp()
        self.verified_name_admin = VerifiedNameAdmin(VerifiedName, AdminSite())
        self.verified_name_config_admin = VerifiedNameConfigAdmin(
            VerifiedNameConfig, AdminSite()
        )

    def test_verified_name_admin(self):
        request = mock.Mock()

        expected_list_display = (
            'id', 'user', 'verified_name', 'verification_attempt_id', 'proctored_exam_attempt_id',
            'is_verified', 'created', 'modified',
        )
        self.assertEqual(
            expected_list_display,
            self.verified_name_admin.get_list_display(request)
        )

        expected_readonly_fields = ('id', 'user', 'created', 'modified')
        self.assertEqual(
            expected_readonly_fields,
            self.verified_name_admin.get_readonly_fields(request)
        )

        expected_search_fields = (
            'user__username', 'verification_attempt_id', 'proctored_exam_attempt_id',
        )
        self.assertEqual(
            expected_search_fields,
            self.verified_name_admin.get_search_fields(request)
        )

    def test_verified_name_config_admin(self):
        request = mock.Mock()

        expected_list_display = (
            'id', 'user', 'use_verified_name_for_certs', 'change_date',
        )
        self.assertEqual(
            expected_list_display,
            self.verified_name_config_admin.get_list_display(request)
        )

        expected_readonly_fields = ('change_date',)
        self.assertEqual(
            expected_readonly_fields,
            self.verified_name_config_admin.get_readonly_fields(request)
        )

        expected_search_fields = ('user__username',)
        self.assertEqual(
            expected_search_fields,
            self.verified_name_config_admin.get_search_fields(request)
        )

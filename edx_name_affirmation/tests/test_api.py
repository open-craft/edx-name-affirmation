"""
Tests for the `edx_name_affirmation` Python API.
"""

import ddt

from django.contrib.auth import get_user_model
from django.test import TestCase

from edx_name_affirmation.api import create_verified_name, get_verified_name
from edx_name_affirmation.exceptions import VerifiedNameEmptyString, VerifiedNameMultipleAttemptIds

User = get_user_model()


@ddt.ddt
class TestVerifiedNameAPI(TestCase):
    """
    Tests for the VerifiedName API.
    """
    VERIFIED_NAME = 'Jonathan Doe'
    PROFILE_NAME = 'Jon Doe'

    def setUp(self):
        super().setUp()
        self.user = User(username='jondoe', email='jondoe@test.com')
        self.user.save()

    def test_create_verified_name_defaults(self):
        """
        Test to create a verified name with default values.
        """
        create_verified_name(
            self.user, self.VERIFIED_NAME, self.PROFILE_NAME,
        )

        verified_name_obj = get_verified_name(self.user)

        self.assertEqual(verified_name_obj.user, self.user)
        self.assertIsNone(verified_name_obj.verification_attempt_id)
        self.assertIsNone(verified_name_obj.proctored_exam_attempt_id)
        self.assertFalse(verified_name_obj.is_verified)

    @ddt.data(
        (123, None, False),
        (None, 456, True),
    )
    @ddt.unpack
    def test_create_verified_name_with_optional_arguments(
        self, verification_attempt_id, proctored_exam_attempt_id, is_verified,
    ):
        """
        Test to create a verified name with optional arguments supplied.
        """
        create_verified_name(
            self.user, self.VERIFIED_NAME, self.PROFILE_NAME, verification_attempt_id,
            proctored_exam_attempt_id, is_verified
        )

        verified_name_obj = get_verified_name(self.user)

        self.assertEqual(verified_name_obj.verification_attempt_id, verification_attempt_id)
        self.assertEqual(verified_name_obj.proctored_exam_attempt_id, proctored_exam_attempt_id)
        self.assertEqual(verified_name_obj.is_verified, is_verified)

    def test_create_verified_name_two_ids(self):
        """
        Test that a verified name cannot be created with both a verification_attempt_id
        and a proctored_exam_attempt_id.
        """
        with self.assertRaises(VerifiedNameMultipleAttemptIds):
            create_verified_name(
                self.user, self.VERIFIED_NAME, self.PROFILE_NAME, 123, 456,
            )

    @ddt.data(
        ('', PROFILE_NAME),
        (VERIFIED_NAME, ''),
    )
    @ddt.unpack
    def test_create_verified_name_empty_string(self, verified_name, profile_name):
        """
        Test that an empty verified_name or profile_name will raise an exception.
        """
        if verified_name == '':
            field = 'verified_name'
        elif profile_name == '':
            field = 'profile_name'

        with self.assertRaises(VerifiedNameEmptyString) as context:
            create_verified_name(self.user, verified_name, profile_name)

        self.assertEqual(
            str(context.exception),
            'Attempted to create VerifiedName for user_id={user_id}, but {field} was '
            'empty.'.format(field=field, user_id=self.user.id),
        )

    def test_get_verified_name_most_recent(self):
        """
        Test to get the most recent verified name.
        """
        create_verified_name(self.user, 'old verified name', 'old profile name')
        create_verified_name(self.user, self.VERIFIED_NAME, self.PROFILE_NAME)

        verified_name_obj = get_verified_name(self.user)

        self.assertEqual(verified_name_obj.verified_name, self.VERIFIED_NAME)
        self.assertEqual(verified_name_obj.profile_name, self.PROFILE_NAME)

    def test_get_verified_name_only_verified(self):
        """
        Test that VerifiedName entries with is_verified=False are ignored if is_verified
        argument is set to True.
        """
        create_verified_name(
            self.user, self.VERIFIED_NAME, self.PROFILE_NAME, is_verified=True
        )
        create_verified_name(self.user, 'unverified name', 'unverified profile name')

        verified_name_obj = get_verified_name(self.user, True)

        self.assertEqual(verified_name_obj.verified_name, self.VERIFIED_NAME)
        self.assertEqual(verified_name_obj.profile_name, self.PROFILE_NAME)

    @ddt.data(False, True)
    def test_get_verified_name_none_exist(self, check_is_verified):
        """
        Test that None returns if there are no VerifiedName entries. If the `is_verified`
        flag is set to True, and there are only non-verified entries, we should get the
        same result.
        """
        if check_is_verified:
            create_verified_name(self.user, self.VERIFIED_NAME, self.PROFILE_NAME)
            verified_name_obj = get_verified_name(self.user, True)
        else:
            verified_name_obj = get_verified_name(self.user)

        self.assertIsNone(verified_name_obj)

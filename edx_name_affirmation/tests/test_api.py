"""
Tests for the `edx_name_affirmation` Python API.
"""

import ddt

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from edx_name_affirmation.api import (
    create_verified_name,
    create_verified_name_config,
    get_verified_name,
    should_use_verified_name_for_certs,
    update_is_verified_status,
    update_verification_attempt_id
)
from edx_name_affirmation.exceptions import (
    VerifiedNameAttemptIdNotGiven,
    VerifiedNameDoesNotExist,
    VerifiedNameEmptyString,
    VerifiedNameMultipleAttemptIds
)
from edx_name_affirmation.models import VerifiedName, VerifiedNameConfig

User = get_user_model()


@ddt.ddt
class TestVerifiedNameAPI(TestCase):
    """
    Tests for the VerifiedName API.
    """
    VERIFIED_NAME = 'Jonathan Doe'
    PROFILE_NAME = 'Jon Doe'
    VERIFICATION_ATTEMPT_ID = 123
    PROCTORED_EXAM_ATTEMPT_ID = 456

    def setUp(self):
        super().setUp()
        self.user = User(username='jondoe', email='jondoe@test.com')
        self.user.save()
        # Create a fresh config with default values
        VerifiedNameConfig.objects.create(user=self.user)

    def tearDown(self):
        super().tearDown()
        cache.clear()

    def test_create_verified_name_defaults(self):
        """
        Test to create a verified name with default values.
        """
        verified_name_obj = self._create_verified_name()

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
        verified_name_obj = self._create_verified_name(
            verification_attempt_id, proctored_exam_attempt_id, is_verified,
        )

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
                self.user,
                self.VERIFIED_NAME,
                self.PROFILE_NAME,
                self.VERIFICATION_ATTEMPT_ID,
                self.PROCTORED_EXAM_ATTEMPT_ID,
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
        self._create_verified_name()

        verified_name_obj = get_verified_name(self.user)

        self.assertEqual(verified_name_obj.verified_name, self.VERIFIED_NAME)
        self.assertEqual(verified_name_obj.profile_name, self.PROFILE_NAME)

    def test_get_verified_name_only_verified(self):
        """
        Test that VerifiedName entries with is_verified=False are ignored if is_verified
        argument is set to True.
        """
        self._create_verified_name(is_verified=True)
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
            self._create_verified_name()
            verified_name_obj = get_verified_name(self.user, True)
        else:
            verified_name_obj = get_verified_name(self.user)

        self.assertIsNone(verified_name_obj)

    def test_update_verification_attempt_id(self):
        """
        Test that the most recent VerifiedName is updated with a verification_attempt_id if
        it does not already have one.
        """
        first_verified_name_id = self._create_verified_name().id
        second_verified_name_id = self._create_verified_name().id

        update_verification_attempt_id(self.user, self.VERIFICATION_ATTEMPT_ID)

        first_verified_name_obj = VerifiedName.objects.get(id=first_verified_name_id)
        second_verified_name_obj = VerifiedName.objects.get(id=second_verified_name_id)

        self.assertIsNone(first_verified_name_obj.verification_attempt_id)
        self.assertEqual(second_verified_name_obj.verification_attempt_id, self.VERIFICATION_ATTEMPT_ID)

    @ddt.data(
        (VERIFICATION_ATTEMPT_ID, None),
        (None, PROCTORED_EXAM_ATTEMPT_ID),
    )
    @ddt.unpack
    def test_update_verification_attempt_id_already_exists(
        self, verification_attempt_id, proctored_exam_attempt_id,
    ):
        """
        Test that if the most recent VerifiedName already has a linked verification or
        proctored exam attempt, a new VerifiedName will be created when updating the
        `verification_attempt_id`.
        """
        self._create_verified_name(
            verification_attempt_id=verification_attempt_id,
            proctored_exam_attempt_id=proctored_exam_attempt_id,
        )
        update_verification_attempt_id(self.user, 789)
        verified_name_qs = VerifiedName.objects.all()
        self.assertEqual(len(verified_name_qs), 2)

    def test_update_verification_attempt_id_none_exist(self):
        """
        Test that if the user does not have an existing VerifiedName,
        `update_verification_attempt_id` will raise an exception.
        """
        with self.assertRaises(VerifiedNameDoesNotExist):
            update_verification_attempt_id(self.user, self.VERIFICATION_ATTEMPT_ID)

    @ddt.data(
        (VERIFICATION_ATTEMPT_ID, None),
        (None, PROCTORED_EXAM_ATTEMPT_ID)
    )
    @ddt.unpack
    def test_update_is_verified_status(
        self, verification_attempt_id, proctored_exam_attempt_id,
    ):
        """
        Test that VerifiedName status can be updated with a given attempt ID.
        """
        self._create_verified_name(verification_attempt_id, proctored_exam_attempt_id)
        update_is_verified_status(
            self.user, True, verification_attempt_id, proctored_exam_attempt_id,
        )
        verified_name_obj = get_verified_name(self.user)
        self.assertTrue(verified_name_obj.is_verified)

    def test_update_is_verified_no_attempt_id(self):
        """
        Test that `update_is_verified_by_attempt_id` will raise an exception with no attempt
        ID given.
        """
        with self.assertRaises(VerifiedNameAttemptIdNotGiven):
            update_is_verified_status(self.user, True)

    def test_update_is_verified_multiple_attempt_ids(self):
        """
        Test that `update_is_verified_by_attempt_id` will raise an exception with multiple attempt
        IDs given.
        """
        with self.assertRaises(VerifiedNameMultipleAttemptIds):
            update_is_verified_status(
                self.user, True, self.VERIFICATION_ATTEMPT_ID, self.PROCTORED_EXAM_ATTEMPT_ID,
            )

    def test_update_is_verified_does_not_exist(self):
        """
        Test that `update_is_verified_by_attempt_id` will raise an exception if a VerifiedName does
        not exist for the attempt ID given.
        """
        with self.assertRaises(VerifiedNameDoesNotExist):
            update_is_verified_status(self.user, True, self.VERIFICATION_ATTEMPT_ID)

    def _create_verified_name(
        self, verification_attempt_id=None, proctored_exam_attempt_id=None, is_verified=False,
    ):
        """
        Util to create and return a VerifiedName with default names.
        """
        create_verified_name(
            self.user, self.VERIFIED_NAME, self.PROFILE_NAME, verification_attempt_id,
            proctored_exam_attempt_id, is_verified
        )
        return get_verified_name(self.user)

    @ddt.data(
        (True, True),
        (True, False),
        (False, False),
    )
    @ddt.unpack
    def test_should_use_verified_name_for_certs(self, create_config, expected_value):
        """
        Test that the correct config value is returned from `should_use_verified_name_for_certs`
        """
        if create_config:
            VerifiedNameConfig.objects.create(user=self.user, use_verified_name_for_certs=expected_value)

        # create config for other user, make sure it is the opposite of the expected value.
        # we want to add an additional config to make sure that caching by user works properly
        other_user = User(username='bobsmith', email='bobsmith@test.com')
        other_user.save()
        VerifiedNameConfig.objects.create(user=other_user, use_verified_name_for_certs=(not expected_value))

        should_use_for_certs = should_use_verified_name_for_certs(self.user)
        self.assertEqual(should_use_for_certs, expected_value)

    def test_create_verified_name_config(self):
        """
        Test that verified name config is created and updated successfully
        """
        create_verified_name_config(self.user, use_verified_name_for_certs=True)

        # check that new record was created
        config_obj = VerifiedNameConfig.current(self.user)
        self.assertTrue(config_obj.use_verified_name_for_certs)
        self.assertEqual(config_obj.user, self.user)

    def test_create_verified_name_config_no_overwrite(self):
        """
        Test that if a field is set to True, it will not be overridden by False
        if not specified when the config is updated
        """
        create_verified_name_config(self.user, use_verified_name_for_certs=True)
        create_verified_name_config(self.user)
        self.assertTrue(should_use_verified_name_for_certs(self.user))

"""
Tests for Name Affirmation signal handlers
"""

import ddt
from edx_toggles.toggles.testutils import override_waffle_flag
from mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from edx_name_affirmation.handlers import idv_attempt_handler, proctoring_attempt_handler
from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.statuses import VerifiedNameStatus
from edx_name_affirmation.toggles import VERIFIED_NAME_FLAG

User = get_user_model()


@override_waffle_flag(VERIFIED_NAME_FLAG, active=True)
class SignalTestCase(TestCase):
    """
    Test case for signals.py
    """

    def setUp(self):  # pylint: disable=super-method-not-called
        self.user = User(username='tester', email='tester@test.com')
        self.user.save()
        self.verified_name = 'Jonathan Smith'
        self.profile_name = 'Jon Smith'
        self.idv_attempt_id = 1111111
        self.proctoring_attempt_id = 2222222


@ddt.ddt
class PostSaveVerifiedNameTests(SignalTestCase):
    """
    Tests for the post_save handler on the VerifiedName model.
    """

    @ddt.data(
      (VerifiedNameStatus.PENDING, False),
      (VerifiedNameStatus.SUBMITTED, False),
      (VerifiedNameStatus.APPROVED, True),
      (VerifiedNameStatus.DENIED, False)
    )
    @ddt.unpack
    def test_post_save_verified_name_approved(self, status, should_send):
        """
        Test that VERIFIED_NAME_APPROVED should only send if the status is changed to approved.
        """
        with patch('edx_name_affirmation.signals.VERIFIED_NAME_APPROVED.send') as mock_signal:
            verified_name_obj = VerifiedName.objects.create(
                user=self.user,
                verified_name='Jonathan Doe',
                profile_name=self.profile_name,
                verification_attempt_id=self.idv_attempt_id
            )
            verified_name_obj.status = status
            verified_name_obj.save()

            self.assertEqual(mock_signal.called, should_send)
            if should_send:
                mock_signal.assert_called_with(
                    sender='name_affirmation', user_id=self.user.id, profile_name=self.profile_name
                )


@ddt.ddt
class IDVSignalTests(SignalTestCase):
    """
    Test for idv_attempt_handler
    """

    def test_idv_create_verified_name(self):
        """
        Test that if no verified name exists for the name or attempt id, create one
        """
        idv_attempt_handler(
            self.idv_attempt_id,
            self.user.id,
            'created',
            self.verified_name,
            self.profile_name
        )

        # make sure that verifiedname is created with relevant data
        verified_name = VerifiedName.objects.get(verification_attempt_id=self.idv_attempt_id)
        self.assertEqual(verified_name.status, VerifiedNameStatus.PENDING)
        self.assertEqual(verified_name.verification_attempt_id, self.idv_attempt_id)
        self.assertEqual(verified_name.verified_name, self.verified_name)
        self.assertEqual(verified_name.profile_name, self.profile_name)

    @ddt.data(
        ('created', VerifiedNameStatus.PENDING),
        ('must_retry', VerifiedNameStatus.PENDING),
        ('submitted', VerifiedNameStatus.SUBMITTED),
        ('approved', VerifiedNameStatus.APPROVED),
        ('denied', VerifiedNameStatus.DENIED)
    )
    @ddt.unpack
    def test_idv_update_multiple_verified_names(self, idv_status, expected_status):
        """
        If a VerifiedName(s) for a user and verified name exist, ensure that it is updated properly
        """
        # create multiple VerifiedNames
        VerifiedName.objects.create(
            user=self.user,
            verified_name=self.verified_name,
            profile_name=self.profile_name,
        )
        VerifiedName.objects.create(
            user=self.user,
            verified_name=self.verified_name,
            profile_name=self.profile_name,
        )
        VerifiedName.objects.create(
            user=self.user,
            verified_name=self.verified_name,
            profile_name=self.profile_name,
            verification_attempt_id=self.idv_attempt_id
        )

        idv_attempt_handler(
            self.idv_attempt_id,
            self.user.id,
            idv_status,
            self.verified_name,
            self.profile_name
        )

        # check that the attempt id and status have been updated for all three VerifiedNames
        self.assertEqual(len(VerifiedName.objects.filter(verification_attempt_id=self.idv_attempt_id)), 3)
        self.assertEqual(len(VerifiedName.objects.filter(status=expected_status)), 3)

    def test_idv_does_not_update_verified_name_by_proctoring(self):
        """
        If the idv handler is triggered, ensure that the idv attempt info does not update any verified name
        records that have a proctoring attempt id
        """
        VerifiedName.objects.create(
            user=self.user,
            verified_name=self.verified_name,
            profile_name=self.profile_name,
            proctored_exam_attempt_id=self.proctoring_attempt_id,
            status=VerifiedNameStatus.DENIED
        )
        VerifiedName.objects.create(
            user=self.user,
            verified_name=self.verified_name,
            profile_name=self.profile_name
        )

        idv_attempt_handler(
            self.idv_attempt_id,
            self.user.id,
            'submitted',
            self.verified_name,
            self.profile_name
        )

        # check that the attempt id and status have only been updated for the record that does not have a proctored
        # exam attempt id
        self.assertEqual(len(VerifiedName.objects.filter(verification_attempt_id=self.idv_attempt_id)), 1)
        self.assertEqual(len(VerifiedName.objects.filter(status=VerifiedNameStatus.SUBMITTED)), 1)

    @ddt.data(
        ('created', VerifiedNameStatus.PENDING),
        ('must_retry', VerifiedNameStatus.PENDING),
        ('submitted', VerifiedNameStatus.SUBMITTED),
        ('approved', VerifiedNameStatus.APPROVED),
        ('denied', VerifiedNameStatus.DENIED)
    )
    @ddt.unpack
    def test_idv_update_one_verified_name(self, idv_status, expected_status):
        """
        If a VerifiedName(s) for a user and verified name exist, ensure that it is updated properly
        """
        with patch('edx_name_affirmation.signals.VERIFIED_NAME_APPROVED.send') as mock_signal:
            VerifiedName.objects.create(
                user=self.user,
                verified_name=self.verified_name,
                profile_name=self.profile_name,
                verification_attempt_id=self.idv_attempt_id
            )

            idv_attempt_handler(
                self.idv_attempt_id,
                self.user.id,
                idv_status,
                self.verified_name,
                self.profile_name
            )

            # check that the attempt id and status have been updated for all three VerifiedNames
            self.assertEqual(len(VerifiedName.objects.filter(verification_attempt_id=self.idv_attempt_id)), 1)
            self.assertEqual(len(VerifiedName.objects.filter(status=expected_status)), 1)

            # If the status is approved, ensure that the post_save signal is called
            if expected_status == VerifiedNameStatus.APPROVED:
                mock_signal.assert_called()
            else:
                with self.assertRaises(AssertionError):
                    mock_signal.assert_called()

    @override_waffle_flag(VERIFIED_NAME_FLAG, active=False)
    def test_idv_handler_with_flag_disabled(self):
        """
        Test that no attempt is created if the waffle flag is disabled
        """

        idv_attempt_handler(
            self.idv_attempt_id,
            self.user.id,
            'submitted',
            self.verified_name,
            self.profile_name
        )

        self.assertEqual(len(VerifiedName.objects.filter()), 0)


@ddt.ddt
class ProctoringSignalTests(SignalTestCase):
    """
    Test for proctoring_attempt_handler
    """

    @ddt.data(
        ('created', VerifiedNameStatus.PENDING),
        ('started', VerifiedNameStatus.PENDING),
        ('submitted', VerifiedNameStatus.SUBMITTED),
        ('verified', VerifiedNameStatus.APPROVED),
        ('rejected', VerifiedNameStatus.DENIED)
    )
    @ddt.unpack
    def test_proctoring_update_status_for_attempt_id(self, proctoring_status, expected_status):
        """
        If a verified name with an attempt ID already exists, update the VerifiedName status
        """
        # create a verified name with an attempt id
        verified_name = VerifiedName.objects.create(
            user=self.user,
            verified_name=self.verified_name,
            profile_name=self.profile_name,
            proctored_exam_attempt_id=self.proctoring_attempt_id,
        )
        object_id = verified_name.id

        proctoring_attempt_handler(
            self.proctoring_attempt_id,
            self.user.id,
            proctoring_status,
            self.verified_name,
            self.profile_name,
            True,
            True,
            True
        )
        # make sure that status on verified name is correct
        verified_name_query = VerifiedName.objects.filter(id=object_id)
        self.assertEqual(len(verified_name_query), 1)
        verified_name = verified_name_query.first()
        self.assertEqual(verified_name.status, expected_status)

    def test_proctoring_create_verified_name(self):
        """
        Test that if no verified name exists for the name or attempt id, create one
        """
        proctoring_attempt_handler(
            self.proctoring_attempt_id,
            self.user.id,
            'created',
            self.verified_name,
            self.profile_name,
            True,
            True,
            True
        )

        # make sure that verifiedname is created with relevant data
        verified_name_query = VerifiedName.objects.filter(proctored_exam_attempt_id=self.proctoring_attempt_id)
        self.assertEqual(len(verified_name_query), 1)
        verified_name = verified_name_query.first()
        self.assertEqual(verified_name.status, VerifiedNameStatus.PENDING)

    # test for log

    @ddt.data(
        (None, None, True, True, True),
        ('John', 'John', False, False, False),
        ('John', 'John', False, True, True),
        ('John', 'John', True, True, False)
    )
    @ddt.unpack
    def test_proctoring_does_not_create_name(
        self,
        verified_name,
        profile_name,
        is_practice,
        is_proctored,
        backend_supports_onboarding
    ):
        """
        Test that if we receive a signal for an attempt id that we do not yet have a verified name for,
        we do not create a verified name under certain conditions.
        """

        # test for signal that does not contain verified or profile name
        proctoring_attempt_handler(
            self.proctoring_attempt_id,
            self.user.id,
            'created',
            verified_name,
            profile_name,
            is_practice,
            is_proctored,
            backend_supports_onboarding
        )

        self.assertEqual(len(VerifiedName.objects.filter()), 0)

    @ddt.data(
        True,
        False
    )
    @patch('logging.Logger.warning')
    def test_proctoring_log_with_existing_approved_verified_name(self, should_names_differ, mock_logger):
        """
        Test that we log a warning when we receive a proctoring signal that has a different full_name
        than the existing approved verified name
        """
        verified_name = VerifiedName.objects.create(
            user=self.user,
            verified_name=self.verified_name,
            profile_name=self.profile_name,
            proctored_exam_attempt_id=self.proctoring_attempt_id,
            status=VerifiedNameStatus.APPROVED
        )

        proctoring_attempt_handler(
            self.proctoring_attempt_id,
            self.user.id,
            'created',
            ('John' if should_names_differ else self.verified_name),
            ('John' if should_names_differ else self.profile_name),
            True,
            True,
            True
        )

        log_str = (
            'Full name for proctored_exam_attempt_id={attempt_id} is not equal to the most recent verified '
            'name verified_name_id={verified_name_id}.'
        ).format(
            attempt_id=self.proctoring_attempt_id,
            verified_name_id=verified_name.id
        )

        self.assertEqual(len(VerifiedName.objects.filter()), 1)
        if should_names_differ:
            mock_logger.assert_called_with(log_str)
        else:
            # check that log is not called if the names do not differ
            with self.assertRaises(AssertionError):
                mock_logger.assert_called_with(log_str)

    @override_waffle_flag(VERIFIED_NAME_FLAG, active=False)
    def test_proctoring_handler_with_flag_disabled(self):
        """
        Test that no attempt is created if the waffle flag is disabled
        """

        proctoring_attempt_handler(
            self.proctoring_attempt_id,
            self.user.id,
            'created',
            self.verified_name,
            self.profile_name,
            True,
            True,
            True
        )

        self.assertEqual(len(VerifiedName.objects.filter()), 0)

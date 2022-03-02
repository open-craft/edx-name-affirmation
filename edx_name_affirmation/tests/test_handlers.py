"""
Tests for Name Affirmation signal handlers
"""

import ddt
from mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from edx_name_affirmation.handlers import (
    idv_attempt_handler,
    idv_delete_handler,
    proctoring_attempt_handler,
    proctoring_delete_handler
)
from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.statuses import VerifiedNameStatus

User = get_user_model()


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
                mock_signal.assert_not_called()

    @ddt.data(
        'ready',
        'must_retry',
    )
    @patch('edx_name_affirmation.tasks.idv_update_verified_name_task.delay')
    def test_idv_non_trigger_status(self, status, mock_task):
        """
        Test that a celery task is not triggered if a non-relevant status is received
        """
        idv_attempt_handler(
            self.idv_attempt_id,
            self.user.id,
            status,
            self.verified_name,
            self.profile_name
        )

        mock_task.assert_not_called()

    @patch('edx_name_affirmation.tasks.delete_verified_name_task.delay')
    def test_idv_delete_handler(self, mock_task):
        """
        Test that a celery task is triggered if an idv delete signal is received
        """
        mock_idv_object = MagicMock()
        mock_idv_object.id = 'abcdef'
        idv_delete_handler(
            {},
            mock_idv_object,
            '',
        )

        mock_task.assert_called_with(mock_idv_object.id, None)


@ddt.ddt
class ProctoringSignalTests(SignalTestCase):
    """
    Test for proctoring_attempt_handler
    """

    @ddt.data(
        ('created', VerifiedNameStatus.PENDING),
        ('submitted', VerifiedNameStatus.SUBMITTED),
        ('verified', VerifiedNameStatus.APPROVED),
        ('rejected', VerifiedNameStatus.DENIED),
        ('error', VerifiedNameStatus.DENIED),
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

    @ddt.data(
        ('verified', VerifiedNameStatus.APPROVED),
        ('rejected', VerifiedNameStatus.DENIED),
    )
    @ddt.unpack
    def test_proctoring_error_update_status(self, proctoring_status, expected_status):
        """
        If we receive a proctoring update with an error status, ensure that later status updates are handled as expected
        """

        proctoring_attempt_handler(
            self.proctoring_attempt_id,
            self.user.id,
            'error',
            self.verified_name,
            self.profile_name,
            True,
            True,
            True
        )

        verified_name = VerifiedName.objects.get(proctored_exam_attempt_id=self.proctoring_attempt_id)
        object_id = verified_name.id
        self.assertEqual(verified_name.status, VerifiedNameStatus.DENIED)

        # update status
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

        # ensure that status is updated for subsequent updates
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

    def test_proctoring_does_not_create_name(self):
        """
        Test that if we receive a signal for an attempt id that we do not have a name for, we do not create a new
        record.
        """

        proctoring_attempt_handler(
            self.proctoring_attempt_id,
            self.user.id,
            'created',
            None,
            None,
            True,
            True,
            True
        )

        self.assertEqual(len(VerifiedName.objects.filter()), 0)

    @ddt.data(
        (False, False, False),
        (False, True, True),
        (True, True, False)
    )
    @ddt.unpack
    @patch('edx_name_affirmation.tasks.proctoring_update_verified_name_task.delay')
    def test_proctoring_does_not_trigger_celery_task(self, is_practice, is_proctored, supports_onboarding, mock_task):
        """
        Test that a celery task is not triggered if the exam does not contain an id verification event
        """
        proctoring_attempt_handler(
            self.proctoring_attempt_id,
            self.user.id,
            'created',
            'John',
            'John',
            is_practice,
            is_proctored,
            supports_onboarding
        )

        mock_task.assert_not_called()

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

    @ddt.data(
        'download_software_clicked',
        'ready_to_start',
        'started',
        'ready_to_submit',
    )
    @patch('edx_name_affirmation.tasks.proctoring_update_verified_name_task.delay')
    def test_proctoring_non_trigger_status(self, status, mock_task):
        """
        Test that a celery task is not triggered if a non-relevant status is received
        """
        proctoring_attempt_handler(
            self.proctoring_attempt_id,
            self.user.id,
            status,
            self.verified_name,
            self.profile_name,
            True,
            True,
            True
        )

        mock_task.assert_not_called()

    @patch('edx_name_affirmation.tasks.delete_verified_name_task.delay')
    def test_proctoring_delete_handler(self, mock_task):
        """
        Test that a celery task is triggered if an idv delete signal is received
        """
        mock_proctoring_object = MagicMock()
        mock_proctoring_object.id = 'abcdef'
        proctoring_delete_handler(
            {},
            mock_proctoring_object,
            '',
        )

        mock_task.assert_called_with(None, mock_proctoring_object.id)

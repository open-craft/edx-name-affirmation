"""
Tests for Name Affirmation tasks
"""

import ddt
from mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.statuses import VerifiedNameStatus
from edx_name_affirmation.tasks import (
    delete_verified_name_task,
    idv_update_verified_name_task,
    proctoring_update_verified_name_task
)

User = get_user_model()


@ddt.ddt
class TaskTests(TestCase):
    """
    Tests for tasks.py
    """
    def setUp(self):  # pylint: disable=super-method-not-called
        self.user = User(username='tester', email='tester@test.com')
        self.user.save()
        self.verified_name_obj = VerifiedName(
          user=self.user, verified_name='Jonathan Doe', profile_name='Jon Doe',
        )
        self.verified_name_obj.save()
        self.idv_attempt_id = 1111111
        self.proctoring_attempt_id = 2222222

    @patch('edx_name_affirmation.tasks.idv_update_verified_name_task.retry')
    def test_idv_retry(self, mock_retry):
        idv_update_verified_name_task.delay(
            self.idv_attempt_id,
            # force an error with an invalid user ID
            99999,
            VerifiedNameStatus.SUBMITTED,
            self.verified_name_obj.verified_name,
            self.verified_name_obj.profile_name,
        )
        mock_retry.assert_called()

    @patch('edx_name_affirmation.tasks.proctoring_update_verified_name_task.retry')
    def test_proctoring_retry(self, mock_retry):
        proctoring_update_verified_name_task.delay(
            self.proctoring_attempt_id,
            # force an error with an invalid user ID
            99999,
            VerifiedNameStatus.PENDING,
            self.verified_name_obj.verified_name,
            self.verified_name_obj.profile_name,
        )
        mock_retry.assert_called()

    def test_idv_delete(self):
        """
        Assert that only relevant VerifiedNames are deleted for a given idv_attempt_id
        """
        # associated test object with an idv attempt
        self.verified_name_obj.verification_attempt_id = self.idv_attempt_id
        self.verified_name_obj.save()

        other_attempt_id = 123456

        # create another VerifiedName with the same idv attempt
        VerifiedName(
            user=self.user,
            verified_name='Jonathan X Doe',
            profile_name='Jon D',
            verification_attempt_id=self.idv_attempt_id
        ).save()

        # create VerifiedName not associated with idv attempt
        other_verified_name_obj = VerifiedName(
            user=self.user,
            verified_name='Jonathan X Doe',
            profile_name='Jon D',
            verification_attempt_id=other_attempt_id
        )
        other_verified_name_obj.save()

        delete_verified_name_task.delay(
            self.idv_attempt_id,
            None
        )

        # check that there is only VerifiedName object
        self.assertEqual(len(VerifiedName.objects.filter(verification_attempt_id=self.idv_attempt_id)), 0)
        self.assertEqual(len(VerifiedName.objects.filter(verification_attempt_id=other_attempt_id)), 1)

    def test_proctoring_delete(self):
        """
        Assert that only relevant VerifiedNames are deleted for a given proctoring_attempt_id
        """
        # associated test object with a proctoring attempt
        self.verified_name_obj.proctored_exam_attempt_id = self.proctoring_attempt_id
        self.verified_name_obj.save()

        other_attempt_id = 123456

        # create another VerifiedName with the same proctoring attempt
        VerifiedName(
            user=self.user,
            verified_name='Jonathan X Doe',
            profile_name='Jon D',
            proctored_exam_attempt_id=self.proctoring_attempt_id
        ).save()

        # create VerifiedName not associated with proctoring attempt
        other_verified_name_obj = VerifiedName(
            user=self.user,
            verified_name='Jonathan X Doe',
            profile_name='Jon D',
            proctored_exam_attempt_id=other_attempt_id
        )
        other_verified_name_obj.save()

        delete_verified_name_task.delay(
            None,
            self.proctoring_attempt_id
        )

        # check that there is only VerifiedName object
        self.assertEqual(len(VerifiedName.objects.filter(proctored_exam_attempt_id=self.proctoring_attempt_id)), 0)
        self.assertEqual(len(VerifiedName.objects.filter(proctored_exam_attempt_id=other_attempt_id)), 1)

    @ddt.data(
        (1234, 5678),
        (None, None)
    )
    @ddt.unpack
    @patch('logging.Logger.error')
    def test_incorrect_args_delete(self, idv_attempt_id, proctoring_attempt_id, mock_logger):
        """
        Assert that error log is called and that no VerifiedNames are deleted when incorrect args are passed to task
        """
        delete_verified_name_task.delay(
            idv_attempt_id,
            proctoring_attempt_id
        )
        mock_logger.assert_called()

    @patch('logging.Logger.info')
    def test_no_names_delete(self, mock_logger):
        delete_verified_name_task.delay(
            self.idv_attempt_id,
            None
        )
        mock_logger.assert_called_with(
            'No VerifiedNames deleted because no VerifiedNames were associated with the provided attempt ID.'
        )

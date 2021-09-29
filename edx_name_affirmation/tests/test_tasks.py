"""
Tests for Name Affirmation tasks
"""

from mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.statuses import VerifiedNameStatus
from edx_name_affirmation.tasks import idv_update_verified_name, proctoring_update_verified_name

User = get_user_model()


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

    @patch('edx_name_affirmation.tasks.idv_update_verified_name.retry')
    def test_idv_retry(self, mock_retry):
        idv_update_verified_name.delay(
            self.idv_attempt_id,
            # force an error with an invalid user ID
            99999,
            VerifiedNameStatus.SUBMITTED,
            self.verified_name_obj.verified_name,
            self.verified_name_obj.profile_name,
        )
        mock_retry.assert_called()

    @patch('edx_name_affirmation.tasks.proctoring_update_verified_name.retry')
    def test_proctoring_retry(self, mock_retry):
        proctoring_update_verified_name.delay(
            self.proctoring_attempt_id,
            # force an error with an invalid user ID
            99999,
            VerifiedNameStatus.PENDING,
            self.verified_name_obj.verified_name,
            self.verified_name_obj.profile_name,
            True,
            True,
            True,
        )
        mock_retry.assert_called()

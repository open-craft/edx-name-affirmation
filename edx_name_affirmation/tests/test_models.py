"""
Tests for Name Affirmation models
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.statuses import VerifiedNameStatus

User = get_user_model()


class VerifiedNameModelTests(TestCase):
    """
    Test suite for the VerifiedName models
    """
    def setUp(self):
        self.verified_name = 'Test Tester'
        self.user = User.objects.create(username='modelTester', email='model@tester.com')
        self.verified_name = VerifiedName.objects.create(
            user=self.user,
            verified_name=self.verified_name,
            status=VerifiedNameStatus.SUBMITTED,
        )
        return super().setUp()

    def test_histories(self):
        """
        Test the model history is recording records as expected
        """
        verified_name_history = self.verified_name.history.all().order_by('history_date')  # pylint: disable=no-member
        assert len(verified_name_history) == 1
        idv_attempt_id = 34455
        self.verified_name.status = VerifiedNameStatus.APPROVED
        self.verified_name.verification_attempt_id = idv_attempt_id
        self.verified_name.save()
        verified_name_history = self.verified_name.history.all().order_by('history_date')  # pylint: disable=no-member
        assert len(verified_name_history) == 2

        first_history_record = verified_name_history[0]
        assert first_history_record.status == VerifiedNameStatus.SUBMITTED
        assert first_history_record.verification_attempt_id is None

        second_history_record = verified_name_history[1]
        assert second_history_record.status == VerifiedNameStatus.APPROVED
        assert second_history_record.verification_attempt_id == idv_attempt_id

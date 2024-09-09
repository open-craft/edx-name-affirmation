"""
Tests for Name Affirmation models
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase

from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.statuses import VerifiedNameStatus

User = get_user_model()


class VerifiedNameModelTests(TestCase):
    """
    Test suite for the VerifiedName models
    """
    def setUp(self):
        self.idv_attempt_id = 34455
        self.idv_attempt_status = 'submitted'
        self.idv_attempt_id_notfound = 404
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

        verified_name_history = self.verified_name.history.all().order_by('history_date')
        assert len(verified_name_history) == 1
        self.verified_name.status = VerifiedNameStatus.APPROVED
        self.verified_name.verification_attempt_id = self.idv_attempt_id
        self.verified_name.save()
        verified_name_history = self.verified_name.history.all().order_by('history_date')
        assert len(verified_name_history) == 2

        first_history_record = verified_name_history[0]
        assert first_history_record.status == VerifiedNameStatus.SUBMITTED
        assert first_history_record.verification_attempt_id is None

        second_history_record = verified_name_history[1]
        assert second_history_record.status == VerifiedNameStatus.APPROVED
        assert second_history_record.verification_attempt_id == self.idv_attempt_id

    @patch('edx_name_affirmation.models.SoftwareSecurePhotoVerification')
    def test_verification_status(self, sspv_mock):
        """
        Test the model history is recording records as expected
        """

        idv_attempt_id_notfound_status = None

        sspv_mock.objects.get = self._mocked_model_get

        self.verified_name.verification_attempt_id = self.idv_attempt_id_notfound
        assert self.verified_name.verification_attempt_status is idv_attempt_id_notfound_status

        self.verified_name.verification_attempt_id = self.idv_attempt_id
        assert self.verified_name.verification_attempt_status is self.idv_attempt_status

    # Helper methods

    def _obj(self, dictionary):
        "Helper method to turn a dict into an object. Used to mock below."

        return type('obj', (object,), dictionary)

    def _mocked_model_get(self, id):  # pylint: disable=redefined-builtin
        "Helper method to mock the behavior of SoftwareSecurePhotoVerification model. Used to mock below."
        if id == self.idv_attempt_id_notfound:
            raise ObjectDoesNotExist

        if id == self.idv_attempt_id:
            return self._obj({'status': self.idv_attempt_status})

        return self._obj({'status': None})

"""
All tests for edx_name_affirmation views
"""
import json

from django.contrib.auth import get_user_model
from django.urls import reverse

from edx_name_affirmation.api import create_verified_name, get_verified_name

from .utils import LoggedInTestCase

User = get_user_model()


class VerifiedNameViewTests(LoggedInTestCase):
    """
    Tests for the VerifiedNameView
    """

    VERIFIED_NAME = 'Jonathan Doe'
    PROFILE_NAME = 'Jon Doe'

    OTHER_VERIFIED_NAME = 'Robert Smith'
    OTHER_PROFILE_NAME = 'Bob Smith'

    def test_verified_name(self):
        create_verified_name(self.user, self.VERIFIED_NAME, self.PROFILE_NAME, is_verified=True)
        verified_name = get_verified_name(self.user, is_verified=True)

        expected_data = {
            'id': verified_name.id,
            'modified': verified_name.modified.isoformat(),
            'created': verified_name.created.isoformat(),
            'user': {'id': self.user.id, 'username': self.user.username, 'email': self.user.email},
            'verified_name': verified_name.verified_name,
            'profile_name': verified_name.profile_name,
            'verification_attempt_id': verified_name.verification_attempt_id,
            'proctored_exam_attempt_id': verified_name.proctored_exam_attempt_id,
            'is_verified': verified_name.is_verified
        }

        response = self.client.get(reverse('edx_name_affirmation:verified_name'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, expected_data)

    def test_staff_access_verified_name(self):
        other_user = User(username='other_tester', email='other@test.com')
        other_user.save()
        create_verified_name(other_user, self.VERIFIED_NAME, self.PROFILE_NAME, is_verified=True)

        # check that non staff access returns 403
        response = self.client.get(reverse('edx_name_affirmation:verified_name'), {'username': other_user.username})
        self.assertEqual(response.status_code, 403)

        self.user.is_staff = True
        self.user.save()

        # create verified name
        create_verified_name(self.user, self.VERIFIED_NAME, self.PROFILE_NAME, is_verified=False)
        other_user_verified_name = get_verified_name(other_user, is_verified=True)

        # expected data should match the verifiedname from the other user
        expected_data = {
            'id': other_user_verified_name.id,
            'modified': other_user_verified_name.modified.isoformat(),
            'created': other_user_verified_name.created.isoformat(),
            'user': {'id': other_user.id, 'username': other_user.username, 'email': other_user.email},
            'verified_name': other_user_verified_name.verified_name,
            'profile_name': other_user_verified_name.profile_name,
            'verification_attempt_id': other_user_verified_name.verification_attempt_id,
            'proctored_exam_attempt_id': other_user_verified_name.proctored_exam_attempt_id,
            'is_verified': other_user_verified_name.is_verified
        }

        response = self.client.get(reverse('edx_name_affirmation:verified_name'), {'username': other_user.username})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, expected_data)

    def test_404_if_no_verified_name(self):
        response = self.client.get(reverse('edx_name_affirmation:verified_name'))
        self.assertEqual(response.status_code, 404)

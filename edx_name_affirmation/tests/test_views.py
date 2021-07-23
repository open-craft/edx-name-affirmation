"""
All tests for edx_name_affirmation views
"""
import json

from edx_toggles.toggles.testutils import override_waffle_flag

from django.contrib.auth import get_user_model
from django.urls import reverse

from edx_name_affirmation.api import create_verified_name, get_verified_name
from edx_name_affirmation.toggles import VERIFIED_NAME_FLAG

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

    ATTEMPT_ID = 11111

    def test_verified_name(self):
        create_verified_name(self.user, self.VERIFIED_NAME, self.PROFILE_NAME, is_verified=True)
        verified_name = get_verified_name(self.user, is_verified=True)

        expected_data = {
            'created': verified_name.created.isoformat(),
            'username': self.user.username,
            'verified_name': verified_name.verified_name,
            'profile_name': verified_name.profile_name,
            'verification_attempt_id': verified_name.verification_attempt_id,
            'proctored_exam_attempt_id': verified_name.proctored_exam_attempt_id,
            'is_verified': verified_name.is_verified,
            'verified_name_enabled': False,
        }

        response = self.client.get(reverse('edx_name_affirmation:verified_name'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, expected_data)

    @override_waffle_flag(VERIFIED_NAME_FLAG, active=True)
    def test_verified_name_feature_enabled(self):
        create_verified_name(self.user, self.VERIFIED_NAME, self.PROFILE_NAME, is_verified=True)
        verified_name = get_verified_name(self.user, is_verified=True)

        expected_data = {
            'created': verified_name.created.isoformat(),
            'username': self.user.username,
            'verified_name': verified_name.verified_name,
            'profile_name': verified_name.profile_name,
            'verification_attempt_id': verified_name.verification_attempt_id,
            'proctored_exam_attempt_id': verified_name.proctored_exam_attempt_id,
            'is_verified': verified_name.is_verified,
            'verified_name_enabled': True,
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
            'created': other_user_verified_name.created.isoformat(),
            'username': other_user.username,
            'verified_name': other_user_verified_name.verified_name,
            'profile_name': other_user_verified_name.profile_name,
            'verification_attempt_id': other_user_verified_name.verification_attempt_id,
            'proctored_exam_attempt_id': other_user_verified_name.proctored_exam_attempt_id,
            'is_verified': other_user_verified_name.is_verified,
            'verified_name_enabled': False,
        }

        response = self.client.get(reverse('edx_name_affirmation:verified_name'), {'username': other_user.username})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode('utf-8'))
        self.assertEqual(data, expected_data)

    def test_404_if_no_verified_name(self):
        response = self.client.get(reverse('edx_name_affirmation:verified_name'))
        self.assertEqual(response.status_code, 404)

    def test_post_200(self):
        verified_name_data = {
            'username': self.user.username,
            'profile_name': self.PROFILE_NAME,
            'verified_name': self.VERIFIED_NAME,
            'verification_attempt_id': self.ATTEMPT_ID,
        }
        response = self.client.post(
            reverse('edx_name_affirmation:verified_name'),
            verified_name_data
        )
        self.assertEqual(response.status_code, 200)

        created_name = get_verified_name(self.user, is_verified=False)
        self.assertEqual(created_name.user.username, self.user.username)
        self.assertEqual(created_name.profile_name, self.PROFILE_NAME)
        self.assertEqual(created_name.verified_name, self.VERIFIED_NAME)
        self.assertEqual(created_name.verification_attempt_id, self.ATTEMPT_ID)

    def test_post_200_if_staff(self):
        self.user.is_staff = True
        self.user.save()

        other_user = User(username='other_tester', email='other@test.com')
        other_user.save()

        verified_name_data = {
            'username': other_user.username,
            'profile_name': self.PROFILE_NAME,
            'verified_name': self.VERIFIED_NAME,
            'proctored_exam_attempt_id': self.ATTEMPT_ID,
            'is_verified': True,
        }
        response = self.client.post(
            reverse('edx_name_affirmation:verified_name'),
            verified_name_data
        )
        self.assertEqual(response.status_code, 200)

        created_name = get_verified_name(other_user, is_verified=True)
        self.assertEqual(created_name.user.username, other_user.username)
        self.assertEqual(created_name.profile_name, self.PROFILE_NAME)
        self.assertEqual(created_name.verified_name, self.VERIFIED_NAME)
        self.assertEqual(created_name.proctored_exam_attempt_id, self.ATTEMPT_ID)

    def test_post_403_non_staff(self):
        other_user = User(username='other_tester', email='other@test.com')
        other_user.save()

        verified_name_data = {
            'username': other_user.username,
            'profile_name': self.PROFILE_NAME,
            'verified_name': self.VERIFIED_NAME,
            'verification_attempt_id': self.ATTEMPT_ID,
            'is_verified': True,
        }
        response = self.client.post(
            reverse('edx_name_affirmation:verified_name'),
            verified_name_data
        )
        self.assertEqual(response.status_code, 403)

    def test_post_400_invalid_serializer(self):
        verified_name_data = {
            'username': self.user.username,
            'profile_name': self.PROFILE_NAME,
            'verified_name': self.VERIFIED_NAME,
            'verification_attempt_id': 'xxyz',
            'is_verified': True
        }
        response = self.client.post(
            reverse('edx_name_affirmation:verified_name'),
            verified_name_data
        )
        self.assertEqual(response.status_code, 400)

    def test_post_400_two_attempt_ids(self):
        verified_name_data = {
            'username': self.user.username,
            'profile_name': self.PROFILE_NAME,
            'verified_name': self.VERIFIED_NAME,
            'verification_attempt_id': self.ATTEMPT_ID,
            'proctored_exam_attempt_id': self.ATTEMPT_ID
        }
        response = self.client.post(
            reverse('edx_name_affirmation:verified_name'),
            verified_name_data
        )
        self.assertEqual(response.status_code, 400)

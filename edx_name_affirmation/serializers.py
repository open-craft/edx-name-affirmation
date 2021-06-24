"""Defines serializers used by the Name Affirmation API"""
from rest_framework import serializers
from rest_framework.fields import DateTimeField

from django.contrib.auth import get_user_model

from edx_name_affirmation.models import VerifiedName

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User Model.
    """
    id = serializers.IntegerField(required=False)  # pylint: disable=invalid-name
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        """
        Meta Class
        """
        model = User

        fields = (
            "id", "username", "email"
        )


class VerifiedNameSerializer(serializers.ModelSerializer):
    """
    Serializer for the VerifiedName Model.
    """
    user = UserSerializer()
    created = DateTimeField(format=None)
    verified_name = serializers.CharField(required=True)
    verification_attempt_id = serializers.IntegerField(required=True, allow_null=True)
    proctored_exam_attempt_id = serializers.IntegerField(required=True, allow_null=True)

    class Meta:
        """
        Meta Class
        """
        model = VerifiedName

        fields = (
            "id", "modified", "created", "user", "verified_name", "profile_name", "verification_attempt_id",
            "proctored_exam_attempt_id", "is_verified"
        )

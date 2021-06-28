"""Defines serializers used by the Name Affirmation API"""
from rest_framework import serializers

from django.contrib.auth import get_user_model

from edx_name_affirmation.models import VerifiedName

User = get_user_model()


class VerifiedNameSerializer(serializers.ModelSerializer):
    """
    Serializer for the VerifiedName Model.
    """
    username = serializers.CharField(source="user.username")
    verified_name = serializers.CharField(required=True)
    profile_name = serializers.CharField(required=True)
    verification_attempt_id = serializers.IntegerField(required=False, allow_null=True)
    proctored_exam_attempt_id = serializers.IntegerField(required=False, allow_null=True)
    is_verified = serializers.BooleanField(required=False, allow_null=True)

    class Meta:
        """
        Meta Class
        """
        model = VerifiedName

        fields = (
            "created", "username", "verified_name", "profile_name", "verification_attempt_id",
            "proctored_exam_attempt_id", "is_verified"
        )

"""
Name Affirmation HTTP-based API endpoints
"""

from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth import get_user_model

from edx_name_affirmation.api import (
    create_verified_name,
    create_verified_name_config,
    get_verified_name,
    get_verified_name_history,
    should_use_verified_name_for_certs
)
from edx_name_affirmation.exceptions import VerifiedNameMultipleAttemptIds
from edx_name_affirmation.serializers import VerifiedNameConfigSerializer, VerifiedNameSerializer
from edx_name_affirmation.statuses import VerifiedNameStatus
from edx_name_affirmation.toggles import is_verified_name_enabled


class AuthenticatedAPIView(APIView):
    """
    Authenticate API View.
    """
    authentication_classes = (SessionAuthentication, JwtAuthentication)
    permission_classes = (IsAuthenticated,)


class VerifiedNameView(AuthenticatedAPIView):
    """
    Endpoint for a VerifiedName.
    /edx_name_affirmation/v1/verified_name?username=xxx

    Supports:
        HTTP POST: Creates a new VerifiedName.
        HTTP GET: Returns an existing VerifiedName (by username or requesting user)

    HTTP POST
    Creates a new VerifiedName.
    Expected POST data: {
        "username": "jdoe",
        "verified_name": "Jonathan Doe"
        "profile_name": "Jon Doe"
        "verification_attempt_id": (Optional)
        "proctored_exam_attempt_id": (Optional)
        "status": (Optional)
    }

    HTTP GET
        ** Scenarios **
        ?username=jdoe
        returns an existing verified name object matching the username
        Example response: {
            "username": "jdoe",
            "verified_name": "Jonathan Doe",
            "profile_name": "Jon Doe",
            "verification_attempt_id": 123,
            "proctored_exam_attempt_id": None,
            "status": "approved",
            "use_verified_name_for_certs": False,
            "verified_name_enabled": True
        }
    """
    def get(self, request):
        """
        Get most recent verified name for the request user or for the specified username
        """
        username = request.GET.get('username')
        if username and not request.user.is_staff:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"detail": "Must be a Staff User to Perform this request."}
            )

        user = get_user_model().objects.get(username=username) if username else request.user
        verified_name = get_verified_name(user, is_verified=True)
        if verified_name is None:
            return Response(
                status=404,
                data={'detail': 'There is no verified name related to this user.'}

            )

        serialized_data = VerifiedNameSerializer(verified_name).data
        serialized_data['verified_name_enabled'] = is_verified_name_enabled()
        serialized_data['use_verified_name_for_certs'] = should_use_verified_name_for_certs(user)
        return Response(serialized_data)

    def post(self, request):
        """
        Create verified name
        """
        username = request.data.get('username')
        if username != request.user.username and not request.user.is_staff:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"detail": "Must be a Staff User to Perform this request."}
            )

        serializer = VerifiedNameSerializer(data=request.data)
        if serializer.is_valid():
            user = get_user_model().objects.get(username=username) if username else request.user
            try:
                create_verified_name(
                    user,
                    request.data.get('verified_name'),
                    request.data.get('profile_name'),
                    verification_attempt_id=request.data.get('verification_attempt_id', None),
                    proctored_exam_attempt_id=request.data.get('proctored_exam_attempt_id', None),
                    status=request.data.get('status', VerifiedNameStatus.PENDING)
                )
                response_status = status.HTTP_200_OK
                data = {}
            except VerifiedNameMultipleAttemptIds as exc:
                response_status = status.HTTP_400_BAD_REQUEST
                data = {"detail": str(exc)}
        else:
            response_status = status.HTTP_400_BAD_REQUEST
            data = serializer.errors
        return Response(status=response_status, data=data)


class VerifiedNameHistoryView(AuthenticatedAPIView):
    """
    Endpoint for VerifiedName history.
    /edx_name_affirmation/v1/verified_name/history?username=xxx

    Supports:
        HTTP GET: Return a list of VerifiedNames for the given user.
    """
    def get(self, request):
        """
        Get a list of verified name objects for the given user, ordered by most recently created.
        """
        username = request.GET.get('username')
        if username and not request.user.is_staff:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"detail": "Must be a Staff User to Perform this request."}
            )

        user = get_user_model().objects.get(username=username) if username else request.user
        verified_name_qs = get_verified_name_history(user)
        serializer = VerifiedNameSerializer(verified_name_qs, many=True)

        serialized_data = {
            'verified_name_enabled': is_verified_name_enabled(),
            'use_verified_name_for_certs': should_use_verified_name_for_certs(user),
            'results': serializer.data,
        }

        return Response(serialized_data)


class VerifiedNameConfigView(AuthenticatedAPIView):
    """
    Endpoint for VerifiedNameConfig.
    /edx_name_affirmation/v1/verified_name/config

    Supports:
        HTTP POST: Creates a new VerifiedNameConfig.

    HTTP POST
    Creates a new VerifiedName.
    Example POST data: {
        "username": "jdoe",
        "use_verified_name_for_certs": True
    }
    """
    def post(self, request):
        """
        Create VerifiedNameConfig
        """
        username = request.data.get('username')
        if username != request.user.username and not request.user.is_staff:
            msg = 'Must be a staff user to override the requested user’s VerifiedNameConfig value'
            return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': msg})

        serializer = VerifiedNameConfigSerializer(data=request.data)

        if serializer.is_valid():
            user = get_user_model().objects.get(username=username) if username else request.user
            create_verified_name_config(
                user,
                use_verified_name_for_certs=request.data.get('use_verified_name_for_certs'),
            )
            response_status = status.HTTP_201_CREATED
            data = {}

        else:
            response_status = status.HTTP_400_BAD_REQUEST
            data = serializer.errors

        return Response(status=response_status, data=data)

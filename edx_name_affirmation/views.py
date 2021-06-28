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

from edx_name_affirmation.api import create_verified_name, get_verified_name
from edx_name_affirmation.exceptions import VerifiedNameMultipleAttemptIds
from edx_name_affirmation.serializers import VerifiedNameSerializer


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
        "is_verified": (Optional)
    }

    HTTP GET
        ** Scenarios **
        ?username=jdoe
        returns an existing verified name object matching the username
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
                    is_verified=request.data.get('is_verified', False)
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

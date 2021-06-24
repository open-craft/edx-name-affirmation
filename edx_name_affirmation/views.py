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

from edx_name_affirmation.api import get_verified_name
from edx_name_affirmation.serializers import VerifiedNameSerializer


class AuthenticatedAPIView(APIView):
    """
    Authenticate API View.
    """
    authentication_classes = (SessionAuthentication, JwtAuthentication)
    permission_classes = (IsAuthenticated,)


class VerifiedNameView(AuthenticatedAPIView):
    """
    Endpoint for getting a verified name and its data.
    /edx_name_affirmation/v1/verified_name?username=xxx
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

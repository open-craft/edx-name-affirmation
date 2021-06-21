"""
Database models for edx_name_affirmation.
"""

from model_utils.models import TimeStampedModel

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class VerifiedName(TimeStampedModel):
    """
    This model represents a verified name for a user, with a link to the source
    through `verification_attempt_id` or `proctored_exam_attempt_id` if applicable.

    .. pii: Contains name fields.
    .. pii_types: name
    .. pii_retirement: local_api
    """
    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)
    verified_name = models.CharField(max_length=255, db_index=True)

    # Snapshot of the user's UserProfile `name` upon creation
    profile_name = models.CharField(max_length=255, null=True)

    # Reference to an external ID verification or proctored exam attempt
    verification_attempt_id = models.PositiveIntegerField(null=True)
    proctored_exam_attempt_id = models.PositiveIntegerField(null=True)

    is_verified = models.BooleanField(default=False)

    class Meta:
        """ Meta class for this Django model """
        db_table = 'nameaffirmation_verifiedname'
        verbose_name = 'verified name'

"""
Database models for edx_name_affirmation.
"""

from config_models.models import ConfigurationModel
from model_utils.models import TimeStampedModel

from django.contrib.auth import get_user_model
from django.db import models

from edx_name_affirmation.statuses import VerifiedNameStatus

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
    verification_attempt_id = models.PositiveIntegerField(null=True, blank=True)
    proctored_exam_attempt_id = models.PositiveIntegerField(null=True, blank=True)

    status = models.CharField(
        max_length=32,
        choices=[(st.value, st.value) for st in VerifiedNameStatus],
        default=VerifiedNameStatus.PENDING.value,
    )

    class Meta:
        """ Meta class for this Django model """
        db_table = 'nameaffirmation_verifiedname'
        verbose_name = 'verified name'


class VerifiedNameConfig(ConfigurationModel):
    """
    This model provides various configuration fields for users regarding their
    verified name.
    .. no_pii: This model has no PII.
    """
    KEY_FIELDS = ('user',)

    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE, related_name='verified_name_config')
    use_verified_name_for_certs = models.BooleanField(default=False)

    class Meta:
        """ Meta class for this Django model """
        db_table = 'nameaffirmation_verifiednameconfig'
        verbose_name = 'verified name config'

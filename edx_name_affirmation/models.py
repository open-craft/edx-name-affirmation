"""
Database models for edx_name_affirmation.
"""
from enum import Enum

from config_models.models import ConfigurationModel
from model_utils.models import TimeStampedModel

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class VerifiedNameStatus(str, Enum):
    """
    Possible states for the verified name.

    Pending: the verified name has been created, but not seen by anyone

    Submitted: the verified name has been submitted to a verification authority

    Approved, Denied: resulting states from that authority

    State transitions in the verifying processes may not move this status.
    For example in proctoring the verification might be pending at exam start,
    unchanged when the exam is ready to submit, move to submitted on submit,
    and then remain unchanged through multiple verification statuses until
    the exam is verified or rejected.

    The expected lifecycle is pending -> submitted -> approved/denied.

    .. no_pii: This model has no PII.
    """
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    DENIED = "denied"


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

    status = models.CharField(
        max_length=32,
        choices=[(st.value, st.value) for st in VerifiedNameStatus],
        default=VerifiedNameStatus.PENDING.value,
    )
    # is_verified is being removed
    is_verified = models.BooleanField(default=False, null=True)

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

"""
Name Affirmation signal handlers
"""

import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.signals import VERIFIED_NAME_APPROVED
from edx_name_affirmation.statuses import VerifiedNameStatus
from edx_name_affirmation.tasks import idv_update_verified_name, proctoring_update_verified_name

User = get_user_model()

log = logging.getLogger(__name__)


@receiver(post_save, sender=VerifiedName)
def verified_name_approved(sender, instance, **kwargs):  # pylint: disable=unused-argument
    """
    Emit a signal when a verified name's status is updated to "approved".
    """
    if instance.status == VerifiedNameStatus.APPROVED:
        VERIFIED_NAME_APPROVED.send(
          sender='name_affirmation',
          user_id=instance.user.id,
          profile_name=instance.profile_name
        )


def idv_attempt_handler(attempt_id, user_id, status, photo_id_name, full_name, **kwargs):
    """
    Receiver for IDV attempt updates

    Args:
        attempt_id(int): ID associated with the IDV attempt
        user_id(int): ID associated with the IDV attempt's user
        status(str): status in IDV language for the IDV attempt
        photo_id_name(str): name to be used as verified name
        full_name(str): user's pending name change or current profile name
    """

    log.info('VerifiedName: idv_attempt_handler triggering Celery task for user %(user_id)s '
             'with photo_id_name %(photo_id_name)s and status %(status)s',
             {
                 'user_id': user_id,
                 'photo_id_name': photo_id_name,
                 'status': status
             }
             )
    idv_update_verified_name.delay(attempt_id, user_id, status, photo_id_name, full_name)


def proctoring_attempt_handler(
    attempt_id,
    user_id,
    status,
    full_name,
    profile_name,
    is_practice_exam,
    is_proctored,
    backend_supports_onboarding,
    **kwargs
):
    """
    Receiver for proctored exam attempt updates.

    Args:
        attempt_id(int): ID associated with the proctored exam attempt
        user_id(int): ID associated with the proctored exam attempt's user
        status(str): status in proctoring language for the proctored exam attempt
        full_name(str): name to be used as verified name
        profile_name(str): user's current profile name
        is_practice_exam(boolean): if the exam attempt is for a practice exam
        is_proctored(boolean): if the exam attempt is for a proctored exam
        backend_supports_onboarding(boolean): if the exam attempt is for an exam with a backend that supports onboarding
    """
    proctoring_update_verified_name.delay(
        attempt_id,
        user_id,
        status,
        full_name,
        profile_name,
        is_practice_exam,
        is_proctored,
        backend_supports_onboarding
    )

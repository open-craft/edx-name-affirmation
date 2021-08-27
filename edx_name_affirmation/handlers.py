# pylint: disable=logging-format-interpolation
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
from edx_name_affirmation.toggles import is_verified_name_enabled

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


def idv_attempt_handler(attempt_id, user_id, status, full_name, profile_name, **kwargs):
    """
    Receiver for IDV attempt updates

    Args:
        attempt_id(int): ID associated with the IDV attempt
        user_id(int): ID associated with the IDV attempt's user
        status(str): status in IDV language for the IDV attempt
        full_name(str): name to be used as verified name
        profile_name(str): user's current profile name
    """
    if not is_verified_name_enabled():
        return

    trigger_status = VerifiedNameStatus.trigger_state_change_from_idv(status)
    verified_names = VerifiedName.objects.filter(user__id=user_id, verified_name=full_name).order_by('-created')
    if verified_names:
        # if there are VerifiedName objects, we want to update existing entries
        # for each attempt with no attempt id (either proctoring or idv), update attempt id
        updated_for_attempt_id = verified_names.filter(
            proctored_exam_attempt_id=None,
            verification_attempt_id=None
        ).update(verification_attempt_id=attempt_id)

        if updated_for_attempt_id:
            log.info(
                'Updated VerifiedNames for user={user_id} to verification_attempt_id={attempt_id}'.format(
                    user_id=user_id,
                    attempt_id=attempt_id,
                )
            )

        # then for all matching attempt ids, update the status
        if trigger_status:
            verified_name_qs = verified_names.filter(
                verification_attempt_id=attempt_id,
                proctored_exam_attempt_id=None
            )

            # Individually update to ensure that post_save signals send
            for verified_name_obj in verified_name_qs:
                verified_name_obj.status = trigger_status
                verified_name_obj.save()

            log.info(
                'Updated VerifiedNames for user={user_id} with verification_attempt_id={attempt_id} to '
                'have status={status}'.format(
                    user_id=user_id,
                    attempt_id=attempt_id,
                    status=trigger_status
                )
            )
    else:
        # otherwise if there are no entries, we want to create one.
        user = User.objects.get(id=user_id)
        verified_name = VerifiedName.objects.create(
            user=user,
            verified_name=full_name,
            profile_name=profile_name,
            verification_attempt_id=attempt_id,
            status=(trigger_status if trigger_status else VerifiedNameStatus.PENDING),
        )
        log.error(
            'Created VerifiedName for user={user_id} to have status={status} '
            'and verification_attempt_id={attempt_id}, because no matching '
            'attempt_id or verified_name were found.'.format(
                user_id=user_id,
                attempt_id=attempt_id,
                status=verified_name.status
            )
        )


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
    if not is_verified_name_enabled():
        return

    # We only care about updates from onboarding exams, or from non-practice proctored exams with a backend that
    # does not support onboarding. This is because those two event types are guaranteed to contain verification events,
    # whereas timed exams and proctored exams with a backend that does support onboarding are not guaranteed
    is_onboarding_exam = is_practice_exam and is_proctored and backend_supports_onboarding
    reviewable_proctored_exam = is_proctored and not is_practice_exam and not backend_supports_onboarding
    if not (is_onboarding_exam or reviewable_proctored_exam):
        return

    # check if approved VerifiedName already exists for the user
    verified_name = VerifiedName.objects.filter(
        user__id=user_id,
        status=VerifiedNameStatus.APPROVED
    ).order_by('-created').first()
    if verified_name:
        approved_verified_name = verified_name.verified_name
        is_full_name_approved = approved_verified_name == full_name
        if not is_full_name_approved:
            log.warning(
                'Full name for proctored_exam_attempt_id={attempt_id} is not equal '
                'to the most recent verified name verified_name_id={name_id}.'.format(
                    attempt_id=attempt_id,
                    name_id=verified_name.id
                )
            )
        return

    trigger_status = VerifiedNameStatus.trigger_state_change_from_proctoring(status)

    verified_name = VerifiedName.objects.filter(
        user__id=user_id,
        proctored_exam_attempt_id=attempt_id
    ).order_by('-created').first()
    if verified_name:
        # if a verified name for the given attempt ID exists, update it if the status should trigger a transition
        if trigger_status:
            verified_name.status = trigger_status
            verified_name.save()
            log.info(
                'Updated VerifiedName for user={user_id} with proctored_exam_attempt_id={attempt_id} '
                'to have status={status}'.format(
                    user_id=user_id,
                    attempt_id=attempt_id,
                    status=trigger_status
                )
            )
    else:
        if full_name and profile_name:
            # if they do not already have an approved VerifiedName, create one
            user = User.objects.get(id=user_id)
            VerifiedName.objects.create(
                user=user,
                verified_name=full_name,
                proctored_exam_attempt_id=attempt_id,
                status=(trigger_status if trigger_status else VerifiedNameStatus.PENDING),
                profile_name=profile_name
            )
            log.info(
                'Created VerifiedName for user={user_id} to have status={status} '
                'and proctored_exam_attempt_id={attempt_id}'.format(
                    user_id=user_id,
                    attempt_id=attempt_id,
                    status=trigger_status
                )
            )
        else:
            log.error(
                'Cannot create VerifiedName for user={user_id} for proctored_exam_attempt_id={attempt_id} '
                'because neither profile name nor full name were provided'.format(
                    user_id=user_id,
                    attempt_id=attempt_id,
                )
            )

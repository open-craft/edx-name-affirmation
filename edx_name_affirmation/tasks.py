# pylint: disable=logging-format-interpolation, unused-argument
"""
Name affirmation celery tasks
"""

import logging

from celery import shared_task
from edx_django_utils.monitoring import set_code_owner_attribute

from django.contrib.auth import get_user_model

from edx_name_affirmation.models import VerifiedName
from edx_name_affirmation.statuses import VerifiedNameStatus

User = get_user_model()

log = logging.getLogger(__name__)

DEFAULT_RETRY_SECONDS = 30
MAX_RETRIES = 3


@shared_task(
    bind=True, autoretry_for=(Exception,), default_retry_delay=DEFAULT_RETRY_SECONDS, max_retries=MAX_RETRIES,
)
@set_code_owner_attribute
def idv_update_verified_name_task(self, attempt_id, user_id, name_affirmation_status, photo_id_name, full_name):
    """
    Celery task for updating a verified name based on an IDV attempt
    """
    log.info('VerifiedName: idv_update_verified_name triggering Celery task started for user %(user_id)s '
             'with attempt_id %(attempt_id)s and status %(status)s',
             {
                'user_id': user_id,
                'attempt_id': attempt_id,
                'status': name_affirmation_status
             }
             )
    verified_names = VerifiedName.objects.filter(user__id=user_id, verified_name=photo_id_name).order_by('-created')
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
        verified_name_qs = verified_names.filter(
            verification_attempt_id=attempt_id,
            proctored_exam_attempt_id=None
        )

        # Individually update to ensure that post_save signals send
        for verified_name_obj in verified_name_qs:
            verified_name_obj.status = name_affirmation_status
            verified_name_obj.save()

        log.info(
            'Updated VerifiedNames for user={user_id} with verification_attempt_id={attempt_id} to '
            'have status={status}'.format(
                user_id=user_id,
                attempt_id=attempt_id,
                status=name_affirmation_status
            )
        )
    else:
        # otherwise if there are no entries, we want to create one.
        user = User.objects.get(id=user_id)
        verified_name = VerifiedName.objects.create(
            user=user,
            verified_name=photo_id_name,
            profile_name=full_name,
            verification_attempt_id=attempt_id,
            status=name_affirmation_status,
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


@shared_task(
    bind=True, autoretry_for=(Exception,), default_retry_delay=DEFAULT_RETRY_SECONDS, max_retries=MAX_RETRIES,
)
@set_code_owner_attribute
def proctoring_update_verified_name_task(
    self,
    attempt_id,
    user_id,
    name_affirmation_status,
    full_name,
    profile_name
):
    """
    Celery task for updating a verified name based on a proctoring attempt
    """

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

    verified_name = VerifiedName.objects.filter(
        user__id=user_id,
        proctored_exam_attempt_id=attempt_id
    ).order_by('-created').first()
    if verified_name:
        verified_name.status = name_affirmation_status
        verified_name.save()
        log.info(
            'Updated VerifiedName for user={user_id} with proctored_exam_attempt_id={attempt_id} '
            'to have status={status}'.format(
                user_id=user_id,
                attempt_id=attempt_id,
                status=name_affirmation_status
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
                status=name_affirmation_status,
                profile_name=profile_name
            )
            log.info(
                'Created VerifiedName for user={user_id} to have status={status} '
                'and proctored_exam_attempt_id={attempt_id}'.format(
                    user_id=user_id,
                    attempt_id=attempt_id,
                    status=name_affirmation_status
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


@shared_task(
    bind=True, autoretry_for=(Exception,), default_retry_delay=DEFAULT_RETRY_SECONDS, max_retries=MAX_RETRIES,
)
@set_code_owner_attribute
def delete_verified_name_task(self, idv_attempt_id, proctoring_attempt_id):
    """
    Celery task to delete a verified name based on an idv or proctoring attempt
    """
    # this case shouldn't happen, but should log as an error in case
    if (idv_attempt_id and proctoring_attempt_id) or (not idv_attempt_id and not proctoring_attempt_id):
        log.error(
            'A maximum of one attempt id should be provided for either a proctored exam attempt or IDV attempt.'
        )
        return

    log_message = {'field_name': '', 'attempt_id': ''}

    if idv_attempt_id:
        verified_names = VerifiedName.objects.filter(verification_attempt_id=idv_attempt_id)
        log_message['field_name'] = 'verification_attempt_id'
        log_message['attempt_id'] = idv_attempt_id
    else:
        verified_names = VerifiedName.objects.filter(proctored_exam_attempt_id=proctoring_attempt_id)
        log_message['field_name'] = 'proctored_exam_attempt_id'
        log_message['attempt_id'] = proctoring_attempt_id

    if verified_names:
        log.info(
            'Deleting {num_names} VerifiedName(s) associated with {field_name}='
            '{verification_attempt_id}'.format(
                num_names=len(verified_names),
                field_name=log_message['field_name'],
                verification_attempt_id=log_message['attempt_id'],
            )
        )
        verified_names.delete()

    log.info(
        'No VerifiedNames deleted because no VerifiedNames were associated with the provided attempt ID.'
    )

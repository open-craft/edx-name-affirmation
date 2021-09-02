"""
Python API for edx_name_affirmation.
"""

import logging

from edx_name_affirmation import toggles
from edx_name_affirmation.exceptions import (
    VerifiedNameAttemptIdNotGiven,
    VerifiedNameDoesNotExist,
    VerifiedNameEmptyString,
    VerifiedNameMultipleAttemptIds
)
from edx_name_affirmation.models import VerifiedName, VerifiedNameConfig
from edx_name_affirmation.statuses import VerifiedNameStatus

log = logging.getLogger(__name__)


def is_verified_name_enabled():
    """
    For callers without direct toggle import available to ask if the verified name feature is enabled.

    Since this uses edx_toggles it expects to be called
    while servicing a request and will check the cached results.
    """
    return toggles.is_verified_name_enabled()


def create_verified_name(
    user, verified_name, profile_name, verification_attempt_id=None,
    proctored_exam_attempt_id=None, status=VerifiedNameStatus.PENDING,
):
    """
    Create a new `VerifiedName` for the given user.

    Arguments:
        * `user` (User object)
        * `verified_name` (str): Representative of the name on the user's physical ID card.
        * `profile_name` (str): A snapshot of either 1) the user's pending name change if given
          or 2) the existing name on the user's profile.
        * `verification_attempt_id` (int): Optional reference to an external ID verification
          attempt.
        * `proctored_exam_attempt_id` (int): Optional reference to an external proctored exam
          attempt.
        * `is_verified` (bool): Optional, defaults False. This should determine whether the
          verified_name is valid for use with ID verification, exams, etc.
    """
    # Do not allow empty strings
    if verified_name == '':
        raise VerifiedNameEmptyString('verified_name', user.id)
    if profile_name == '':
        raise VerifiedNameEmptyString('profile_name', user.id)

    # Only link to one attempt
    if verification_attempt_id and proctored_exam_attempt_id:
        err_msg = (
            'Attempted to create VerifiedName for user_id={user_id}, but two different '
            'external attempt IDs were given. Only one may be used. '
            'verification_attempt_id={verification_attempt_id}, '
            'proctored_exam_attempt_id={proctored_exam_attempt_id}, '
            'status={status}'.format(
                user_id=user.id, verification_attempt_id=verification_attempt_id,
                proctored_exam_attempt_id=proctored_exam_attempt_id, status=status,
            )
        )
        raise VerifiedNameMultipleAttemptIds(err_msg)

    VerifiedName.objects.create(
        user=user,
        verified_name=verified_name,
        profile_name=profile_name,
        verification_attempt_id=verification_attempt_id,
        proctored_exam_attempt_id=proctored_exam_attempt_id,
        status=status,
    )

    log_msg = (
        'VerifiedName created for user_id={user_id}. '
        'verification_attempt_id={verification_attempt_id}, '
        'proctored_exam_attempt_id={proctored_exam_attempt_id}, '
        'status={status}'.format(
            user_id=user.id, verification_attempt_id=verification_attempt_id,
            proctored_exam_attempt_id=proctored_exam_attempt_id, status=status,
        )
    )
    log.info(log_msg)


def get_verified_name(user, is_verified=False):
    """
    Get the most recent VerifiedName for a given user.

    Arguments:
        * `user` (User object)
        * `is_verified` (bool): Optional, set to True to ignore entries that are not
          verified.

    Returns a VerifiedName object.
    """
    verified_name_qs = VerifiedName.objects.filter(user=user).order_by('-created')

    if is_verified:
        return verified_name_qs.filter(status=VerifiedNameStatus.APPROVED.value).first()

    return verified_name_qs.first()


def get_verified_name_history(user):
    """
    Return a QuerySet of all VerifiedNames for a given user, ordered by the date created from
    most recent.

    Arguments:
        * `user` (User object)
    """
    return VerifiedName.objects.filter(user=user).order_by('-created')


def update_verification_attempt_id(user, verification_attempt_id):
    """
    Update the `verification_attempt_id` for the user's most recent VerifiedName.

    If the VerifiedName already has a linked verification or proctored exam attempt, create a new
    VerifiedName instead, using the same `verified_name` and `profile_name`.

    This will raise an exception if the user does not have an existing VerifiedName.

    Arguments:
        * `user` (User object)
        * `verification_attempt_id` (int)
    """
    verified_name_obj = get_verified_name(user)

    if not verified_name_obj:
        err_msg = (
            'Attempted to update most recent VerifiedName for user_id={user_id} with '
            'verification_attempt_id={verification_attempt_id}, but this user does not have '
            'an existing VerifiedName.'.format(
                user_id=user.id, verification_attempt_id=verification_attempt_id
            )
        )
        raise VerifiedNameDoesNotExist(err_msg)

    if verified_name_obj.verification_attempt_id or verified_name_obj.proctored_exam_attempt_id:
        log_msg = (
            'Attempted to update VerifiedName id={id} with '
            'verification_attempt_id={verification_attempt_id}, but it already has a linked attempt. '
            'Creating a new VerifiedName for user_id={user_id}'.format(
                id=verified_name_obj.id, verification_attempt_id=verification_attempt_id, user_id=user.id,
            )
        )
        log.warning(log_msg)

        create_verified_name(
            user=user,
            verified_name=verified_name_obj.verified_name,
            profile_name=verified_name_obj.profile_name,
            verification_attempt_id=verification_attempt_id,
        )

    verified_name_obj.verification_attempt_id = verification_attempt_id
    verified_name_obj.save()

    log_msg = (
        'Updated VerifiedName id={id} with verification_attempt_id={verification_attempt_id} '
        'for user_id={user_id}'.format(
            id=verified_name_obj.id, verification_attempt_id=verification_attempt_id, user_id=user.id,
        )
    )
    log.info(log_msg)


def update_verified_name_status(
    user, status, verification_attempt_id=None, proctored_exam_attempt_id=None
):
    """
    Update the status of a VerifiedName using the linked ID verification or exam attempt ID. Only one
    of these should be specified.

    Arguments:
        * user (User object)
        * status (Verified Name Status)
        * verification_attempt_id (int)
        * proctored_exam_attempt_id (int)
    """
    filters = {'user': user}

    if verification_attempt_id:
        if proctored_exam_attempt_id:
            err_msg = (
                'Attempted to update the status for a VerifiedName, but two different '
                'attempt IDs were given. verification_attempt_id={verification_attempt_id}, '
                'proctored_exam_attempt_id={proctored_exam_attempt_id}'.format(
                    verification_attempt_id=verification_attempt_id,
                    proctored_exam_attempt_id=proctored_exam_attempt_id,
                )
            )
            raise VerifiedNameMultipleAttemptIds(err_msg)
        filters['verification_attempt_id'] = verification_attempt_id
    elif proctored_exam_attempt_id:
        filters['proctored_exam_attempt_id'] = proctored_exam_attempt_id
    else:
        err_msg = (
            'Attempted to update the status for a VerifiedName, but no '
            'verification_attempt_id or proctored_exam_attempt_id was given.'
        )
        raise VerifiedNameAttemptIdNotGiven(err_msg)

    verified_name_obj = VerifiedName.objects.filter(**filters).order_by('-created').first()

    if not verified_name_obj:
        err_msg = (
            'Attempted to update status={status} for a VerifiedName, but one does '
            'not exist for the given attempt ID. verification_attempt_id={verification_attempt_id}, '
            'proctored_exam_attempt_id={proctored_exam_attempt_id}'.format(
                status=status,
                verification_attempt_id=verification_attempt_id,
                proctored_exam_attempt_id=proctored_exam_attempt_id,
            )
        )
        raise VerifiedNameDoesNotExist(err_msg)

    verified_name_obj.status = status.value
    verified_name_obj.save()

    log_msg = (
        'Updated status={status} for VerifiedName belonging to user_id={user_id}. '
        'verification_attempt_id={verification_attempt_id}, '
        'proctored_exam_attempt_id={proctored_exam_attempt_id}'.format(
            status=status,
            user_id=verified_name_obj.user.id,
            verification_attempt_id=verification_attempt_id,
            proctored_exam_attempt_id=proctored_exam_attempt_id,
        )
    )
    log.info(log_msg)


def create_verified_name_config(user, use_verified_name_for_certs=None):
    """
    Create verified name configuration for the given user.
    Arguments:
        * `user` (User object)
        * `use_verified_name_for_certs` (bool): If True, certificates will prioritize
          the user's verified name over their profile name.
    """
    fields = {'user': user}

    # Default to the values from the most recent config
    existing_config = VerifiedNameConfig.objects.filter(user=user).order_by('-change_date').first()
    if existing_config:
        fields['use_verified_name_for_certs'] = existing_config.use_verified_name_for_certs

    if use_verified_name_for_certs is not None:
        fields['use_verified_name_for_certs'] = use_verified_name_for_certs

    config_obj = VerifiedNameConfig.objects.create(**fields)

    log_msg = (
        'Created verified name config for user_id={user_id} with '
        'use_verified_name_for_certs={use_verified_name_for_certs}'.format(
            user_id=config_obj.user.id,
            use_verified_name_for_certs=config_obj.use_verified_name_for_certs,
        )
    )
    log.info(log_msg)


def should_use_verified_name_for_certs(user):
    """
    Returns a boolean describing whether the user has opted to use their verified
    name over their profile name for certificates.
    Arguments:
        * `user` (User object)
    """
    config_obj = VerifiedNameConfig.current(user)
    return config_obj.use_verified_name_for_certs

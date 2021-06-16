"""
Python API for edx_name_affirmation.
"""

import logging

from edx_name_affirmation.exceptions import VerifiedNameEmptyString, VerifiedNameMultipleAttemptIds
from edx_name_affirmation.models import VerifiedName

log = logging.getLogger(__name__)


def create_verified_name(
    user, verified_name, profile_name, verification_attempt_id=None,
    proctored_exam_attempt_id=None, is_verified=False,
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
            'is_verified={is_verified}'.format(
                user_id=user.id, verification_attempt_id=verification_attempt_id,
                proctored_exam_attempt_id=proctored_exam_attempt_id, is_verified=is_verified,
            )
        )
        raise VerifiedNameMultipleAttemptIds(err_msg)

    VerifiedName.objects.create(
        user=user,
        verified_name=verified_name,
        profile_name=profile_name,
        verification_attempt_id=verification_attempt_id,
        proctored_exam_attempt_id=proctored_exam_attempt_id,
        is_verified=is_verified,
    )

    log_msg = (
        'VerifiedName created for user_id={user_id}. '
        'verification_attempt_id={verification_attempt_id}, '
        'proctored_exam_attempt_id={proctored_exam_attempt_id}, '
        'is_verified={is_verified}'.format(
            user_id=user.id, verification_attempt_id=verification_attempt_id,
            proctored_exam_attempt_id=proctored_exam_attempt_id, is_verified=is_verified,
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
        return verified_name_qs.filter(is_verified=True).first()

    return verified_name_qs.first()

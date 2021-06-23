"""
Custom exceptions for edx_name_affirmation.
"""


class VerifiedNameDoesNotExist(Exception):
    """
    The requested VerifiedName does not exist.
    """


class VerifiedNameEmptyString(Exception):
    """
    An empty string was supplied for verified_name or profile_name.

    Arguments:
        * field (str): 'verified_name' or 'profile_name'
        * user_id (int)
    """

    def __init__(self, field, user_id):
        self.field = field
        self.user_id = user_id
        super().__init__(self.field, self.user_id)

    def __str__(self):
        return (
            'Attempted to create VerifiedName for user_id={user_id}, but {field} was '
            'empty.'.format(field=self.field, user_id=self.user_id)
        )


class VerifiedNameMultipleAttemptIds(Exception):
    """
    Both a verification_attempt_id and proctored_exam_attempt_id were supplied for
    the same VerifiedName.
    """


class VerifiedNameAttemptIdNotGiven(Exception):
    """
    Neither a verification_attempt_id or a proctored_exam_attempt_id was given for a
    function that requires it.
    """

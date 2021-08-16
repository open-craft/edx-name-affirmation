"""
Statuses for edx_name_affirmation.
"""

from enum import Enum


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

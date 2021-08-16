"""
Statuses for edx_name_affirmation.
"""

from enum import Enum


class VerifiedNameStatus(str, Enum):
    """
    Possible states for the verified name.

    Pending: the verified name has been created

    Submitted: the verified name has been submitted to a verification authority

    Approved, Denied: resulting states from that authority

    This is the status of the verified name attempt, which is related to
    but separate from the status of the verifying process such as IDV or proctoring.
    Status changes in the verifying processes are usually more fine grained.

    For example when proctoring changes from ready to start to started the verified
    name is still pending. Once proctoring is actually submitted the verified name
    can be considered submitted.

    The expected lifecycle is pending -> submitted -> approved/denied.

    .. no_pii: This model has no PII.
    """
    PENDING = "pending"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    DENIED = "denied"

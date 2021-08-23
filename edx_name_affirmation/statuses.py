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

    @classmethod
    def trigger_state_change_from_idv(cls, idv_status):
        """
        Return the translated IDV status if it should trigger a state transition, otherwise return None
        """
        # mapping from an idv status (key) to it's associated verified name status (value). We only want to
        # include idv statuses that would cause a status transition for a verified name
        idv_state_transition_mapping = {
            'created': cls.PENDING,
            'submitted': cls.SUBMITTED,
            'approved': cls.APPROVED,
            'denied': cls.DENIED
        }

        return idv_state_transition_mapping.get(idv_status, None)

    @classmethod
    def trigger_state_change_from_proctoring(cls, proctoring_status):
        """
        Return the translated proctoring status if it should trigger a state transition, otherwise return None
        """
        # mapping from an proctoring status (key) to it's associated verified name status (value). We only want to
        # include proctoring statuses that would cause a status transition for a verified name
        proctoring_state_transition_mapping = {
            'created': cls.PENDING,
            'submitted': cls.SUBMITTED,
            'verified': cls.APPROVED,
            'rejected': cls.DENIED
        }

        return proctoring_state_transition_mapping.get(proctoring_status, None)

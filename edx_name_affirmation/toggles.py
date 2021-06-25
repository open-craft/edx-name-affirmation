"""
Toggles for edx-name-affirmation app
"""

from edx_toggles.toggles import WaffleFlag

# .. toggle_name: name_affirmation.verified_name
# .. toggle_implementation: WaffleFlag
# .. toggle_default: False
# .. toggle_description: Enable the verified name feature
# .. toggle_use_cases: temporary
# .. toggle_creation_date: 2021-06-30
# .. toggle_target_removal_date: None
# .. toggle_tickets: MST-801
VERIFIED_NAME_FLAG = WaffleFlag('name_affirmation.verified_name', __name__)


def is_verified_name_enabled():
    return VERIFIED_NAME_FLAG.is_enabled()

"""
Name Affirmation signals
"""

from django.dispatch import Signal

VERIFIED_NAME_APPROVED = Signal(providing_args=['user_id', 'profile_name'])

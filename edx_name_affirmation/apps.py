"""
edx_name_affirmation Django application initialization.
"""

from django.apps import AppConfig


class EdxNameAffirmationConfig(AppConfig):
    """
    Configuration for the edx_name_affirmation Django application.
    """

    name = 'edx_name_affirmation'

    plugin_app = {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'edx_name_affirmation',
                'regex': '^api/',
                'relative_path': 'urls',
            }
        }
    }

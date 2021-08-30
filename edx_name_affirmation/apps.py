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
        },
        'signals_config': {
            'lms.djangoapp': {
                'relative_path': 'handlers',
                'receivers': [
                    {
                        'receiver_func_name': 'idv_attempt_handler',
                        'signal_path': 'lms.djangoapps.verify_student.signals.idv_update_signal',
                    },
                    {
                        'receiver_func_name': 'proctoring_attempt_handler',
                        'signal_path': 'edx_proctoring.signals.exam_attempt_status_signal',
                    }
                ],
            }
        }
    }

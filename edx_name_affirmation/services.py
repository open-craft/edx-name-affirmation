"""
Name Affirmation Service
"""

import types


class NameAffirmationService:
    """
    Service to expose Name Affirmation API methods
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        This is a class factory to make sure this is a Singleton.
        """
        if not cls._instance:
            cls._instance = super(NameAffirmationService, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """
        Class initializer, which just inspects the libraries and exposes the same functions
        as a direct pass through.
        """
        # pylint: disable=import-outside-toplevel
        from edx_name_affirmation import api as edx_name_affirmation_api
        self._bind_to_module_functions(edx_name_affirmation_api)

    def _bind_to_module_functions(self, module):
        """
        Bind module functions.
        """
        for attr_name in dir(module):
            attr = getattr(module, attr_name, None)
            if isinstance(attr, types.FunctionType):
                if not hasattr(self, attr_name):
                    setattr(self, attr_name, attr)

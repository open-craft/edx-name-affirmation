"""
Tests for name change validator
"""


import ddt

from django.test import TestCase

from edx_name_affirmation.name_change_validator import NameChangeValidator


@ddt.ddt
class NameChangeValidatorTests(TestCase):
    """
    Tests for name_change_validator.py
    """

    @ddt.data(
        ('Jonathan Adams', 'Jon Adams'),
        ('Jonathan Adams', 'Jonathan Quincy Adams'),
        ('Jonathan Adams', 'Jon at han Adams'),
        ('Jonathan Adams', 'Jonathan  Adams'),
        ('Jonathan Adams', 'Jonathan Adens')
    )
    @ddt.unpack
    def test_name_update_requires_idv_invalid_edits(self, old_name, new_name):
        """
        Test that a name change is blocked through this API if it requires ID verification.
        In this case, the user has invalid name edits
        """
        validator = NameChangeValidator([], 1, old_name, new_name)
        self.assertFalse(validator.validate())

    def test_name_update_requires_idv_name_changes(self):
        """
        Test that a name change is blocked through this API if it requires ID verification.
        In this case, the user has previously changed their name 2 or more times
        """
        validator = NameChangeValidator(['Old Name 1'], 1, 'Old Name 2', 'New Name')
        self.assertFalse(validator.validate())

    @ddt.data(
        ('Jonathan Adams', 'Jonathan Q Adams'),
        ('Jonathan Adams', 'Jonathan Adam'),
        ('Jonathan Adams', 'Jo nathan Adams'),
        ('Jonathan Adams', 'Jonatha N Adams'),
        ('Jonathan Adams', 'Jonathan Adáms'),
        ('Jonathan Adáms', 'Jonathan Adæms'),
        ('Jonathan Adams', 'Jonathan A\'dams'),
        ('李陈', '李王')
    )
    @ddt.unpack
    def test_name_update_does_not_require_idv_valid_edits(self, old_name, new_name):
        """
        Test that the user can change their name freely if it does not require verification.
        """
        validator = NameChangeValidator([], 1, old_name, new_name)
        self.assertTrue(validator.validate())

    def test_name_update_does_not_require_idv_no_certificate(self):
        """
        Test that the user can change their name freely if they have no certificates
        """
        validator = NameChangeValidator(['Really Old Name', 'Very Old Name'], 0, 'Old Name', 'New Name')
        self.assertTrue(validator.validate())

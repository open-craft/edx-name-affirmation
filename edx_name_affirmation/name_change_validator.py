"""
Name Change Validator
"""

import re
from difflib import SequenceMatcher


class NameChangeValidator:
    """
    Class used to validate name changes
    """

    # maximum number of name changes allowed before verification should be triggered
    MAX_NUM_NAME_CHANGES = 2

    def __init__(self, old_names_list, num_certs, old_name, new_name):
        """
        Class initializer
        """
        self.old_names_list = old_names_list
        self.num_certs = num_certs
        self.old_name = old_name
        self.new_name = new_name

    def _validate_spaces(self):
        """
        Validate spaces in a new name

        Returns a boolean representing if spaces within string follow current rules
        """
        contains_multiple_spaces = bool(re.search(r' {2,}', self.new_name))
        if contains_multiple_spaces:
            return False
        return True

    def _validate_string_changes(self):
        """
        Validate any changes made from the old name to the new name

        Returns a boolean representing if the changes follow current rules
        Edits are considered invalid if:
            * Two or more spaces occur in a row
            * More than one non-space character is added/removed/replaced (exception for if a space
              is added on either side of the non-space character)
        """
        modifications = 0
        # get differences between old name and new name
        sequence = SequenceMatcher(lambda x: x == " ", self.old_name, self.new_name)
        for tag, i1, i2, j1, j2 in sequence.get_opcodes():
            # if there is more than one sequence in the string that has been modified, edits are invalid
            if modifications > 1:
                return False

            # if tag is anything other than equal, increase modifications
            if tag != 'equal':
                modifications += 1

                # determine which piece has been modified
                old_name_substring = self.old_name[i1:i2]
                new_name_substring = self.new_name[j1:j2]
                modified_substring = (
                    old_name_substring
                    if len(old_name_substring) > len(new_name_substring)
                    else new_name_substring
                )
                is_valid = bool(re.search(r'^\s?(\S\s?)?$', modified_substring))
                if not is_valid:
                    return False

        return True

    def _validate_old_name_changes(self):
        """
        Validate that a user has not changed their name more than the maximum number allowed
        """
        return len(self.old_names_list) < self.MAX_NUM_NAME_CHANGES

    def _validate_num_certs(self):
        """
        Validate that the user does not have any certificates
        """
        return self.num_certs == 0

    def validate(self):
        """
        Return a boolean representing if the edits to a name are valid and follow the current rules for validation
        """
        return (
            self._validate_num_certs()  # if a user has no certs, changes will always be considered valid
            or (
                self._validate_spaces()
                and self._validate_string_changes()
                and self._validate_old_name_changes()
            )
        )

"""
File for constans definitions.
"""
from enum import IntEnum


class AccessLevel(IntEnum):
    """
    Class that defines access for tags
    The more higher the class, the most restrictions has.
    """
    PUBLIC = 1
    PROTECTED = 2
    PRIVATE = 3

    @classmethod
    def choices(cls):
        """Returns choices for the class"""
        return [(key.value, key.name) for key in cls]  # pylint: disable=not-an-iterable

    @classmethod
    def get_choice(cls, value):
        """Function that gets choice value for AccessLevel"""
        for key in cls:  # pylint: disable=not-an-iterable
            if key.value == value:
                return key.name
        return None


class Status(IntEnum):
    """
    Class that defines status for tags.
    When a tag is created, is created with a valid tag, when someone soft deletes
    the tag, then is marked as invalid.
    """
    VALID = 1
    INVALID = 0

    @classmethod
    def choices(cls):
        """Returns choices for the class."""
        return [(key.value, key.name) for key in cls]  # pylint: disable=not-an-iterable

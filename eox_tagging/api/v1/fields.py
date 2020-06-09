"""Module for defining custom fields."""
from rest_framework import serializers


class EnumField(serializers.ChoiceField):
    """Serializer field for choices."""
    def __init__(self, enum, **kwargs):
        self.enum = enum
        kwargs['choices'] = [(e.value, e.name) for e in enum]
        super(EnumField, self).__init__(**kwargs)

    def to_representation(self, obj):
        """Function that helps with choice serialization."""
        try:
            value = obj.name
            return value
        except AttributeError:
            return self.enum(obj).name

    def to_internal_value(self, data):
        """Function that helps with choice deserialization."""
        try:
            return self.enum[data]
        except KeyError:
            self.fail('invalid_choice', input=data)
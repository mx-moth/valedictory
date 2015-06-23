from __future__ import absolute_import, unicode_literals

import copy
import functools

from gettext import gettext as _

from .exceptions import (
    ValidationErrors, ValidationException, NoData, NestedValidatorException)
from .fields import Field


def partition_dict(d, pred, dict_class=dict):
    """
    Split a dict in two based on a predicate. ``d`` is a dict (or dict-like)
    object. ``pred(key, value)`` is a function that returns a bool, which will
    determine which dict the key, value pair will be sent to. Returns two
    dicts, ``(false, true)``, where ``false`` is a dict with all pairs where
    ``pred`` returned ``False``, and ``true`` is a dict with all pairs where
    ``pred`` returned ``True``.
    """
    def iterator(acc, pair):
        f, t = acc
        key, val = pair
        if pred(key, val):
            t[key] = val
        else:
            f[key] = val
        return f, t
    return functools.reduce(iterator, d.items(), (dict_class(), dict_class()))


class DeclarativeFieldsMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        # Split out any fields declared on this Validator
        attrs, new_fields = partition_dict(
            attrs, lambda k, v: isinstance(v, Field))

        # Make the class
        cls = super(DeclarativeFieldsMetaclass, mcs).__new__(
            mcs, name, bases, attrs)

        # Set the declared fields to the `fields` attribute, merging in any
        # existing fields
        fields = {}
        field_sets = [getattr(base, 'fields', {}) for base in reversed(cls.__mro__)]
        field_sets.append(new_fields)
        for field_set in field_sets:
            if field_set is None:
                continue
            for name, field in field_set.items():
                fields[name] = copy.copy(field)
        setattr(cls, 'fields', fields)

        return cls


class BaseValidator(object):
    """
    Validate an input dict against a set of validators, which ensure that the
    data is of the correct input type, format, and value, and return a
    (possibly modified) value for output.
    """

    # A ``dict`` of ``"name": Field()`` entries.
    fields = None

    # Whether or not unknown fields being present in the input data is
    # considered an error.
    allow_unknown_fields = False

    default_error_messages = {
        'unknown': _('Unknown field'),
    }

    def __init__(self, fields=None, allow_unknown_fields=None,
                 error_messages=None):
        if fields is not None:
            self.fields = self.fields.copy()
            self.fields.update(fields)

        if allow_unknown_fields is not None:
            self.allow_unknown_fields = allow_unknown_fields

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

    def clean(self, data):
        """
        Take the form data supplied, and clean it using the validators

        Returns the cleaned and validated data
        """
        errors = ValidationErrors()
        cleaned_data = {}

        # Check for unknown fields
        if not self.allow_unknown_fields:
            for name in data.keys():
                if name not in self.fields:
                    errors[name].append(self.error_messages['unknown'])

        # Validate all incoming fields
        for name, field in self.fields.items():
            try:
                datum = data.get(name, NoData)
                value = field.clean(datum)
                cleaned_data[name] = value

            except NestedValidatorException as err:
                errors[name] = err.msg

            except ValidationException as err:
                errors[name].extend(err.msg)

            except NoData:
                pass

        if errors:
            return None, errors
        else:
            return cleaned_data, None

    def __getitem__(self, key):
        return self.fields[key]


class Validator(BaseValidator, metaclass=DeclarativeFieldsMetaclass):
    pass

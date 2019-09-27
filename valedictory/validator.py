import copy
import functools
from gettext import gettext as _

from .base import ErrorMessageMixin
from .exceptions import BaseValidationException, InvalidDataException, NoData
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
                fields[name] = copy.deepcopy(field)
        setattr(cls, 'fields', fields)

        return cls


class BaseValidator(ErrorMessageMixin):
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
        'unknown': _("Unknown field"),
    }

    def __init__(self, fields=None, allow_unknown_fields=None,
                 error_messages=None, **kwargs):
        super().__init__(error_messages=error_messages, **kwargs)

        self.fields = copy.deepcopy(self.fields)
        if fields is not None:
            self.fields.update(fields)

        if allow_unknown_fields is not None:
            self.allow_unknown_fields = allow_unknown_fields

    def clean(self, data, *args, **kwargs):
        """
        Take input data, validate that it conforms to the required schema,
        and return the cleaned output.

        If the data does not conform to the required schema,
        an :exc:`~valedictory.exceptions.InvalidDataException` will be raised.
        """
        cleaned_data, errors = self.clean_fields(data, *args, **kwargs)

        if errors:
            raise errors
        else:
            return cleaned_data

    def clean_fields(self, data):
        errors = InvalidDataException()
        cleaned_data = {}
        # Check for unknown fields
        if not self.allow_unknown_fields:
            unknown_fields = set(data.keys()) - set(self.fields.keys())
            for name in unknown_fields:
                errors.invalid_fields[name].append(self.error('unknown'))

        # Validate all incoming fields
        for name, field in self.fields.items():
            try:
                datum = data.get(name, NoData)
                value = field.clean(datum)
                cleaned_data[name] = value

            except NoData:
                pass

            except BaseValidationException as err:
                errors.invalid_fields[name].append(err)

        return cleaned_data, errors

    def __getitem__(self, key):
        return self.fields[key]

    def __deepcopy__(self, memo):
        obj = super().__deepcopy__(memo)
        obj.fields = copy.deepcopy(self.fields, memo)
        return obj


class Validator(BaseValidator, metaclass=DeclarativeFieldsMetaclass):
    pass

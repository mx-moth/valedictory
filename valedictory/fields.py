import copy
import datetime
import re
from decimal import Decimal
from gettext import gettext as _

import aniso8601

from .base import ErrorMessageMixin
from .exceptions import BaseValidationException, InvalidDataException, NoData


class Field(ErrorMessageMixin):
    """
    The base class for all fields.
    By itself, :class:`~Field` only enforces the :attr:`Field.required` behaviour.
    Subclasses of :class:`~Field` add more validation rules to add more useful behaviours.

    **Attributes**

    .. autoattribute:: required
    .. autoattribute:: default
        :annotation:

    .. autoattribute:: default_error_messages
        :annotation:

    **Methods**

    .. automethod:: clean
    .. automethod:: error
    """

    #: Is this field required to be present in the data.
    #:
    #: If a field is not required, and is not present in the data,
    #: it will not be present in the cleaned data either.
    #: If a field is required, and is not present in the data,
    #: a :exc:`~valedictory.exceptions.ValidationException` will be thrown.
    required = True

    #: The default for this field if no value is supplied. Can be ``None``. If
    #: not set, there is no default and the field will not be present in the
    #: cleaned data.
    default = NoData

    #: A dictionary of messages for each error this field can raise.
    #: The default error messages can be overridden by passing an
    #: ``error_messages`` dict to the constructor.
    #:
    #: required
    #:     Raised when the field is not in the input data,
    #:     but the field is required.
    default_error_messages = {
        'required': _("This field is required"),
    }

    def __init__(self, required=None, error_messages=None, **kwargs):
        if 'default' in kwargs:
            self.default = kwargs.pop('default')

        super().__init__(error_messages=error_messages, **kwargs)

        if required is not None:
            self.required = required

        if self.required and self.has_default:
            raise ValueError("A field cannot have a default and be required")

    @property
    def has_default(self):
        return self.default is not NoData

    def clean(self, data):
        """
        Clean and validate the given data.

        If there is no data for the field,
        pass in the :exc:`~valedictory.exceptions.NoData` class to signal this.
        If the field is required, a
        :exc:`~valedictory.exceptions.ValidationException` will be raised.
        If the field is not required, :exc:`~valedictory.exceptions.NoData` is returned.
        """
        if data is NoData:
            if self.has_default:
                data = self.default
            elif self.required:
                raise self.error('required')
            else:
                raise NoData
        return data


class TypedField(Field):
    """
    A :class:`Field` that requires a specific type of input, such as
    strings, integers, or booleans.

    .. autoattribute:: required_types
        :annotation:

    .. autoattribute:: excluded_types
        :annotation:

    .. autoattribute:: type_name
        :annotation:

    .. autoattribute:: default_error_messages
        :annotation:
    """

    #: A tuple of acceptable classes for the data.
    #: For example, ``(int, float)`` would accept any number type.
    required_types = ()

    #: A tuple of unacceptable classes for the data.
    #: For example, ``bool``\s are subclasses of ``int``\s,
    #: but should not be accepted as valid data when a number is expected.
    excluded_types = ()

    #: The friendly name of the type for error messages.
    type_name = u''

    #:
    #: invalid_type
    #:     Raised when the incoming data is not an instance of :attr:`required_types`,
    #:     or is a subclass of :attr:`excluded_types`.
    default_error_messages = {
        'invalid_type': _("Expected a value of type '{type}'"),
    }

    def __init__(self, *, required_types=None, excluded_types=None,
                 type_name=None, **kwargs):
        super().__init__(**kwargs)

        if required_types is not None:
            self.required_types = required_types
        if required_types is not None:
            self.required_types = required_types
        if type_name is not None:
            self.type_name = type_name

    def clean(self, data):
        value = super(TypedField, self).clean(data)

        if (not isinstance(value, self.required_types) or
                isinstance(value, self.excluded_types)):
            raise self.error('invalid_type', {'type': self.type_name})

        return value


class StringField(TypedField):
    """
    Accepts a string, and only strings.

    .. autoattribute:: min_length

    .. autoattribute:: max_length

    .. autoattribute:: default_error_messages
        :annotation:
    """
    required_types = (str,)

    type_name = u'string'

    #: The minimum acceptable length of the string.
    #: Defaults to no minimum length.
    min_length = 0

    #: The maximum acceptable length of the string.
    #: Defaults to no maximum length.
    max_length = float('inf')

    #:
    #: non_empty
    #:     Raised when the input is an empty string, but :attr:`min_length` is 1.
    #:
    #: min_length
    #:     Raised when the input is shorter than :attr:`min_length`.
    #:
    #: max_length
    #:     Raised when the input is longer than :attr:`max_length`.
    default_error_messages = {
        'non_empty': _("This field can not be empty"),
        'min_length': _("Minimum length {min}"),
        'max_length': _("Maximum length {max}"),
    }

    def __init__(self, min_length=None, max_length=None, **kwargs):
        """
        Construct a field that accepts only strings.

        In addition to the arguments accepted by the ``Field`` class, the
        following arguments are accepted:

        * The ``min_length`` and ``max_length`` keyword arguments set the
          minimum and maximum length of string the field will accept.
        """
        super(StringField, self).__init__(**kwargs)

        if min_length is not None:
            self.min_length = min_length
        if max_length is not None:
            self.max_length = max_length

    def clean(self, data):
        value = super(StringField, self).clean(data)
        if value == u'' and self.required:
            raise self.error('required')

        if len(value) < self.min_length:
            if self.min_length == 1:
                raise self.error('non_empty')
            else:
                raise self.error('min_length', {'min': self.min_length})

        if len(value) > self.max_length:
            raise self.error('max_length', {'max': self.max_length})

        return value


class BooleanField(TypedField):
    """
    A field that only accepts True and False values.
    """
    required_types = bool
    type_name = u'boolean'


class NumberField(TypedField):
    """
    A field that only accepts numbers, either floats or integers.

    .. autoattribute:: min

    .. autoattribute:: max

    .. autoattribute:: default_error_messages
        :annotation:
    """
    required_types = (int, float, Decimal, complex)
    excluded_types = bool  # bools subclass ints :(
    type_name = u'number'

    #: The minimum allowable value. Values lower than this will raise an exception.
    #: Defaults to no minimum value.
    min = None

    #: The maximum allowable value. Values higher than this will raise an exception.
    #: Defaults to no maximum value.
    max = None

    #:
    #: min_value
    #:     Raised when the value is lower than :attr:`min`.
    #:
    #: max_value
    #:     Raised when the value is higher than :attr:`max`.
    default_error_messages = {
        'min_value': _("This must be equal to or greater than the minimum of {min}"),
        'max_value': _("This must be equal to or less than the maximum of {max}"),
    }

    def __init__(self, min=None, max=None, **kwargs):
        """
        In addition to the arguments accepted by the ``Field`` class, the
        following arguments are accepted:

        * The ``min`` and ``max`` keyword arguments set the minimum and maximum
          value the field will accept. The range is inclusive.
        """
        super().__init__(**kwargs)
        if min is not None:
            self.min = min

        if max is not None:
            self.max = max

    def clean(self, data):
        value = super().clean(data)

        if self.min is not None and value < self.min:
            raise self.error('min_value', {'min': self.min})

        if self.max is not None and value > self.max:
            raise self.error('max_value', {'max': self.max})

        return value


class IntegerField(NumberField):
    """
    A :class:`NumberField` that only accepts integers.
    """
    required_types = int
    excluded_types = bool  # bools subclass ints :(
    type_name = u'integer'


class FloatField(NumberField):
    """
    A :class:`NumberField` that only accepts floating point numbers.
    """
    required_types = float
    type_name = u'float'


class EmailField(StringField):
    """
    A :class:`StringField` that only accepts email address strings. The email matching regular
    expression only checks for basic conformance: the string must have at least
    one character, then an '@' symbol, then more characters with at least one
    dot.

    .. autoattribute:: default_error_messages
        :annotation:
    """

    email_re = re.compile(r"[^@]+@[^@]+\.[^@]+")

    #:
    #: invalid_email
    #:     Raised when the data is not a valid email address.
    default_error_messages = {
        'invalid_email': _("Not a valid email address"),
    }

    def clean(self, data):
        value = super(EmailField, self).clean(data)
        if not self.email_re.match(value):
            raise self.error('invalid_email')
        return value


class DateTimeField(StringField):
    """
    A field that only accepts ISO 8601 date time strings.

    After cleaning, a ``datetime.datetime`` instance is returned.

    .. autoattribute:: timezone_required
        :annotation:

    .. autoattribute:: default_error_messages
        :annotation:
    """

    # YYYY-MM-DDTHH:MM:SS.ssssss+00:00 = 32 chars.
    max_length = 32

    #: If a timezone is required. If this is ``False``, naive datetimes will be
    #: allowed.
    timezone_required = True

    #:
    #: invalid_format
    #:     Raised when the input is not a valid ISO8601-formatted date time
    #: no_timezone
    #:     Raised when the input does not have a timezone specified, but
    #:     :attr:`timezone_required` is ``True``
    default_error_messages = {
        'invalid_format': _("Not a valid date time"),
        'no_timezone': _("A timezone must be specified"),
    }

    def __init__(self, *, timezone_required=None, **kwargs):
        super().__init__(**kwargs)

        if timezone_required is not None:
            self.timezone_required = timezone_required

    def clean(self, data):
        date_string = super(DateTimeField, self).clean(data)

        try:
            value = aniso8601.parse_datetime(date_string)
        except (ValueError, NotImplementedError):
            raise self.error('invalid_format')

        if self.timezone_required and value.tzinfo is None:
            raise self.error('no_timezone')

        return value


class DateField(StringField):
    """
    A field that only accepts ISO 8601 date strings.

    After cleaning, a ``datetime.date`` instance is returned.

    .. autoattribute:: default_error_messages
        :annotation:
    """

    # YYYY-MM-DD = 10 chars.
    max_length = 10

    #:
    #: invalid_format
    #:     Raised when the input is not a valid date
    default_error_messages = {
        'invalid_format': _("Not a valid date"),
    }

    def clean(self, data):
        date_string = super(DateField, self).clean(data)
        try:
            return aniso8601.parse_date(date_string)
        except ValueError:
            raise self.error('invalid_format')


class TimeField(StringField):
    """
    A field that only accepts ISO 8601 time strings.

    After cleaning, a ``datetime.time`` instance is returned.

    .. autoattribute:: timezone_required
        :annotation:

    .. autoattribute:: default_error_messages
        :annotation:
    """

    # HH:MM:SS.ssssss+00:00 = 11 chars.
    max_length = 21

    #: If a timezone is required. If this is ``False``, naive times will be
    #: allowed.
    timezone_required = True

    #:
    #: invalid_format
    #:     Raised when the input is not a valid ISO8601-formatted date time
    #: no_timezone
    #:     Raised when the input does not have a timezone specified, but
    #:     :attr:`timezone_required` is ``True``
    default_error_messages = {
        'invalid_format': _("Not a valid time"),
        'no_timezone': _("A timezone must be specified"),
    }

    def __init__(self, *, timezone_required=None, **kwargs):
        super().__init__(**kwargs)

        if timezone_required is not None:
            self.timezone_required = timezone_required

    def clean(self, data):
        time_string = super(DateTimeField, self).clean(data)

        try:
            value = aniso8601.parse_time(time_string)
        except (ValueError, NotImplementedError):
            raise self.error('invalid_format')

        if self.timezone_required and value.tzinfo is None:
            raise self.error('no_timezone')

        return value


class YearMonthField(StringField):
    """
    A field that only accepts ``YYYY-MM`` date strings.

    After cleaning, a tuple of ``(year, month)`` integers are returned.

    .. autoattribute:: default_error_messages
        :annotation:
    """

    # YYYY-MM = 7 chars.
    max_length = 7

    #:
    #: invalid_format
    #:     Raised when the input is not a valid year-month tuple
    default_error_messages = {
        'invalid_format': _("Not a valid date"),
    }

    def clean(self, data):
        date_string = super(YearMonthField, self).clean(data)

        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m").date()
        except ValueError:
            raise self.error('invalid_format')

        return (date.year, date.month)


class ChoiceField(Field):
    """
    A field that only accepts values from a predefined set of choices.
    The values can be of any hashable type.

    .. autoattribute:: choices
        :annotation: = set()

    .. autoattribute:: default_error_messages
        :annotation:
    """

    #: The field will only accept data if the value is in this set.
    choices = None

    #:
    #: invalid_choice
    #:     Raised when the value is not one of the valid choices
    default_error_messages = {
        'invalid_choice': _("Not a valid choice"),
    }

    def __init__(self, choices=None, **kwargs):
        super(ChoiceField, self).__init__(**kwargs)
        if choices is not None:
            self.choices = set(choices)

    def clean(self, data):
        value = super(ChoiceField, self).clean(data)
        try:
            if value not in self.choices:
                raise self.error('invalid_choice')
        except TypeError:
            # ``{} in set()`` throws a TypeError: unhashable type: 'dict'
            raise self.error('invalid_choice')

        return value

    def __deepcopy__(self, memo):
        obj = super().__deepcopy__(memo)
        obj.choices = copy.deepcopy(obj.choices, memo)
        return obj


class ChoiceMapField(Field):
    """
    A field that only accepts values from a predefined dictionary of choices.
    The dictionary maps from valid input choices to the cleaned value returned.

    For example:

    .. code:: python

        >>> field = ChoiceMapField({1: 'one', 2: 'two', 3: 'three'})
        >>> field.clean(1)
        'one'
        >>> field.clean("one")
        valedictory.exceptions.ValidationException: Not a valid choice


    would only accept one of the numbers 1, 2 or 3 as input,
    and would return one of the strings "one", "two", or "three".

    .. autoattribute:: choices
        :annotation: = set()

    .. autoattribute:: default_error_messages
        :annotation:
    """

    #: The field will only accept data if the value is in this set.
    choices = None

    #:
    #: invalid_choice
    #:     Raised when the value is not one of the valid choices
    default_error_messages = {
        'invalid_choice': _("Not a valid choice"),
    }

    def __init__(self, choices=None, **kwargs):
        super(ChoiceMapField, self).__init__(**kwargs)
        if choices is not None:
            self.choices = dict(choices)

    def clean(self, data):
        value = super(ChoiceMapField, self).clean(data)
        try:
            return self.choices[value]
        except (KeyError, TypeError):
            # self.choices[{}] throws a TypeError: unhashable type: 'dict'
            raise self.error('invalid_choice')

    def __deepcopy__(self, memo):
        obj = super().__deepcopy__(memo)
        obj.choices = copy.deepcopy(obj.choices, memo)
        return obj


class PunctuatedCharacterField(TypedField):
    """
    A field that accepts characters only from an alphabet of allowed
    characters. A set of allowed punctuation characters are allowed and
    discarded when cleaned.

    .. autoattribute:: alphabet
        :annotation:

    .. autoattribute:: punctuation
        :annotation:

    .. autoattribute:: min_length

    .. autoattribute:: max_length

    .. autoattribute:: default_error_messages
        :annotation:
    """

    required_types = (str)
    type_name = u'string'

    #: A string of all the allowed characters,
    #: not including :attr:`punctuation` characters.
    #: The cleaned output will consist only of characters from this string.
    alphabet = None

    #: A string of all the punctuation characters allowed.
    #: Punctuation characters will be removed from the cleaned output.
    punctuation = None

    #: The minimum length of the cleaned output data,
    #: not including punctuation characters.
    #: There is no minimum length by default.
    min_length = 0

    #: The maximum length of the cleaned output data,
    #: not including punctuation characters.
    #: There is no maximum length by default.
    max_length = float('inf')

    #:
    #: allowed_characters
    #:     Raised when characters not in
    #:     :attr:`alphabet` or :attr:`punctuation` are in the input.
    #:
    #: min_length
    #:     Raised when the cleaned string is shorter than :attr:`min_length`.
    #:
    #: max_length
    #:     Raised when the cleaned string is longer than :attr:`max_length`.
    default_error_messages = {
        'allowed_characters': _("Only the characters '{alphabet}{punctuation}' are allowed"),
        'min_length': _("Minimum length {min}"),
        'max_length': _("Maximum length {max}"),
    }

    def __init__(self, alphabet=None, punctuation=None,
                 min_length=None, max_length=None, **kwargs):
        """
        Construct a new PunctuatedCharacterField.

        In addition to the arguments accepted by the ``Field`` class, the
        following arguments are accepted:

        * ``alphabet`` is a string of allowed characters.
        * ``puctuation`` is a string of allowed punctuation characters that
          will be stripped as part of validation.
        * ``min_length`` and ``max_length`` are the minimum and maximum allowed
          number of characters. Length is calculated *after* punctuation
          characters are removed.
        """
        super(PunctuatedCharacterField, self).__init__(**kwargs)

        if alphabet is not None:
            self.alphabet = str(alphabet)
        if punctuation is not None:
            self.punctuation = str(punctuation)

        if min_length is not None:
            self.min_length = min_length
        if max_length is not None:
            self.max_length = max_length

    def clean(self, data):
        value = super(PunctuatedCharacterField, self).clean(data)

        # Strip out punctuation
        alphabet_dict = dict((ord(c), None) for c in self.alphabet)
        punctuation_dict = dict((ord(c), None) for c in self.punctuation)

        value = value.translate(punctuation_dict)
        stripped_value = value.translate(alphabet_dict)

        if len(stripped_value) != 0:
            raise self.error('allowed_characters', {
                'alphabet': self.alphabet,
                'punctuation': self.punctuation})

        if len(value) < self.min_length:
            raise self.error('min_length', {'min': self.min_length})

        if len(value) > self.max_length:
            raise self.error('max_length', {'max': self.max_length})

        return value


class RestrictedCharacterField(PunctuatedCharacterField):
    """
    A field that only allows a defined alphabet of characters to be used.

    This is just a :class:`PunctuatedCharacterField`,
    with :attr:`~PunctuatedCharacterField.punctuation` set to the empty string.

    .. attribute:: alphabet

        A string of the characters allowed in the input.
        If the input contains a character not in this string,
        a :exc:`~valedictory.exceptions.ValidationException` is raised.
    """

    punctuation = ''


class DigitField(RestrictedCharacterField):
    """
    A field that only allows strings made up of digits.
    It is not treated as a number, and leading zeros are preserved.
    """
    alphabet = '0123456789'


class CreditCardField(PunctuatedCharacterField):
    """
    Accepts credit card numbers.
    The credit card numbers are checked using the Luhn checksum.

    The credit card number can optionally be punctuated by `" -"` characters.

    .. autoattribute:: default_error_messages
        :annotation:
    """
    punctuation = ' -'
    alphabet = '0123456789'

    min_length = 12
    max_length = 20

    #:
    #: luhn_checksum
    #:     Raised when the credit card is not valid,
    #:     according to the Luhn checksum
    default_error_messages = {
        'luhn_checksum': _("The credit card number is not valid"),
    }

    def clean(self, data):
        value = super(CreditCardField, self).clean(data)

        if not self.luhn_checksum(value):
            raise self.error('luhn_checksum')

        return value

    def luhn_checksum(self, card_number):
        digits = list(map(int, reversed(card_number)))
        evens = sum(digits[0::2])
        odds = sum(sum(divmod(digit * 2, 10)) for digit in digits[1::2])
        return (evens + odds) % 10 == 0


class ListField(TypedField):
    """
    A list field validates all elements of a list against a field.
    For example, to accept a list of integers,
    you could declare a :class:`ListField` like:

    .. code:: python

        class MyValidator(Validator):
            numbers = ListField(IntegerField())

    .. autoattribute:: field
        :annotation:

    """

    #: The field to validate all elements of the input data against.
    field = None

    required_types = list
    type_name = 'list'

    def __init__(self, field=None, **kwargs):
        """
        Construct a new ListField

        In addition to the arguments accepted by the ``Field`` class, the
        following arguments are accepted:

        * ``field`` should be an instance of a Field subclass. Each item in the
          submitted list will be validated and cleaned with Field.
        """
        super(ListField, self).__init__(**kwargs)

        if field is not None:
            self.field = field

    def clean(self, data):
        value = super(ListField, self).clean(data)

        errors = InvalidDataException()
        cleaned_list = []
        for i, datum in enumerate(value):
            try:
                cleaned_list.append(self.field.clean(datum))
            except BaseValidationException as err:
                errors.invalid_fields[i].append(err)

        if errors:
            raise errors
        return cleaned_list

    def __deepcopy__(self, memo):
        obj = super().__deepcopy__(memo)
        obj.field = copy.deepcopy(self.field, memo)
        return obj


class NestedValidator(TypedField):
    """
    Nested validators allow nesting dicts inside one another.
    A validator is used to validate and clean the nested dict.
    To validate a person with structured address data,
    you could make a :class:`~valedictory.Validator` like:

    .. code:: python

        class AddressValidator(Validator):
            street = StringField(min_length=1)
            suburb = StringField(min_length=1)
            postcode = DigitField(min_length=4, max_length=4)
            state = ChoiceField('ACT NSW NT QLD SA TAS VIC WA'.split())

        class Person(Validator):
            name = StringField()
            address = NestedValidator(AddressValidator())

    This would accept data like:

    .. code:: json

        {
            "name": "Alex Smith",
            "address": {
                "street": "123 Example Street",
                "suburb": "Example Burb",
                "postcode": "7123",
                "state": "TAS"
            }
        }
    """
    required_types = (dict, )
    type_name = 'object'

    def __init__(self, validator=None, **kwargs):
        """
        Construct a new NestedValidator

        In addition to the arguments accepted by the ``Field`` class, the
        following arguments are accepted:

        * ``validator`` should be an instance of a Validator class. The nested
          dict is passed to this validator for validation and cleaning.
        """
        super(NestedValidator, self).__init__(**kwargs)

        if validator is not None:
            self.validator = validator

    def clean(self, data):
        value = super(NestedValidator, self).clean(data)
        return self.validator.clean(value)

    def __deepcopy__(self, memo):
        obj = super().__deepcopy__(memo)
        obj.validator = copy.deepcopy(self.validator, memo)
        return obj

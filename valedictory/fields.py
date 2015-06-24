import datetime
import re

from gettext import gettext as _

from .exceptions import (
    BaseValidationException, InvalidDataException, ValidationException, NoData)


class Field(object):
    required = True

    default_error_messages = {
        "required": _("This field is required"),
    }

    def __init__(self, required=True, error_messages=None):
        self.required = required

        messages = {}
        for c in reversed(self.__class__.__mro__):
            messages.update(getattr(c, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

    def clean(self, data):
        if data is NoData:
            if self.required:
                raise ValidationException(self.error_messages['required'])
            else:
                raise NoData
        return data

    def __copy__(self, **kwargs):
        return self.__class__(required=self.required, **kwargs)


class TypedField(Field):
    """
    Base Field class for fields that require a specific type of input, such as
    strings, integers, or booleans.
    """
    required_types = ()
    excluded_types = ()
    type_name = u''

    default_error_messages = {
        "invalid_type": _("This field must be a {type}"),
    }

    def clean(self, data):
        value = super(TypedField, self).clean(data)

        if (not isinstance(value, self.required_types) or
                isinstance(value, self.excluded_types)):
            raise ValidationException(
                self.error_messages["invalid_type"].format(
                    type=self.type_name))

        return value


class StringField(TypedField):
    """
    Accepts a string, and only strings.
    """
    required_types = str
    type_name = u'string'
    min_length = 0
    max_length = float('inf')

    default_error_messages = {
        "non_empty": "This field can not be empty",
        "min_length": "Minimum length {0}",
        "max_length": "Maximum length {0}",
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
            raise ValidationException(self.error_messages['required'])

        if len(value) < self.min_length:
            if self.min_length == 1:
                raise ValidationException(self.error_messages['non_empty'])
            else:
                raise ValidationException(
                    self.error_messages['min_length'].format(self.min_length))

        if len(value) > self.max_length:
            raise ValidationException(
                self.error_messages['max_length'].format(self.max_length))

        return value

    def __copy__(self, **kwargs):
        return super(StringField, self).__copy__(min_length=self.min_length,
                                                 max_length=self.max_length)


class BooleanField(TypedField):
    """
    A field that only accepts True and False values.
    """
    required_types = bool
    type_name = u'boolean'


class IntegerField(TypedField):
    """
    A field that only accepts integer values.
    """
    required_types = int
    excluded_types = bool  # bools subclass ints :(
    type_name = u'integer'
    default_error_messages = {
        'min_value': _("This must be equal to or greater than the minimum of {0}"),
        'max_value': _("This must be equal to or less than the maximum of {0}"),
    }

    def __init__(self, min=None, max=None, *args, **kwargs):
        """
        Construct a field that accepts only integers.

        In addition to the arguments accepted by the ``Field`` class, the
        following arguments are accepted:

        * The ``min`` and ``max`` keyword arguments set the minimum and maximum
          value the field will accept. The range is inclusive.
        """
        super(IntegerField, self).__init__(*args, **kwargs)
        self.min = min
        self.max = max

    def clean(self, data):
        value = super(IntegerField, self).clean(data)

        if self.min is not None and value < self.min:
            raise ValidationException(
                self.error_messages['min_value'].format(self.min))

        if self.max is not None and value > self.max:
            raise ValidationException(
                self.error_messages['max_value'].format(self.max))

        return value

    def __copy__(self, **kwargs):
        return super(IntegerField, self).__copy__(min=self.min,
                                                  max=self.max)


class EmailField(StringField):
    """
    A field that only accepts email address strings. The email matching regular
    expression only checks for basic conformance: the string must have at least
    one character, then an '@' symbol, then more characters with at least one
    dot.
    """

    email_re = re.compile(r"[^@]+@[^@]+\.[^@]+")

    default_error_messages = {
        'invalid_email': _("Not a valid email address"),
    }

    def clean(self, data):
        value = super(EmailField, self).clean(data)
        if not self.email_re.match(value):
            raise ValidationException(self.error_messages['invalid_email'])
        return value


class DateField(StringField):
    """
    A field that only accepts ISO 8601 date strings.

    After cleaning, a ``datetime.date`` instance is returned.
    """

    # YYYY-MM-DD = 10 chars.
    max_length = 10

    default_error_messages = {
        'invalid_date': _("Not a valid date"),
    }

    def clean(self, data):
        date_string = super(DateField, self).clean(data)

        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationException(self.error_messages['invalid_date'])

        return date


class YearMonthField(StringField):
    """
    A field that only accepts ``YYYY-MM`` date strings.

    After cleaning, a tuple of ``(year, month)`` instance is returned.
    """

    # YYYY-MM = 9 chars.
    # Support 6 digit years, to keep the long now/y10k people happy
    max_length = 9

    default_error_messages = {
        'invalid_date': _("Not a valid date"),
    }

    def clean(self, data):
        date_string = super(YearMonthField, self).clean(data)

        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m").date()
        except ValueError:
            raise ValidationException(self.error_messages['invalid_date'])

        return (date.year, date.month)


class ChoiceField(Field):
    """
    A field that only accepts values from a predefined list. The values can be
    of any type.
    """

    default_error_messages = {
        'invalid_choice': _("Not a valid choice"),
    }

    def __init__(self, choices, **kwargs):
        """
        Construct a ChoiceField.

        In addition to the arguments accepted by the ``Field`` class, the
        following arguments are accepted:

        * ``choices`` must be an iterable of choices. The field will only
          accept data if the value is in this list.
        """
        super(ChoiceField, self).__init__(**kwargs)
        self.choices = list(choices)

    def clean(self, data):
        value = super(ChoiceField, self).clean(data)
        if value not in self.choices:
            raise ValidationException(self.error_messages['invalid_choice'])
        return value

    def __copy__(self, **kwargs):
        return super(ChoiceField, self).__copy__(choices=self.choices)


class PunctuatedCharacterField(TypedField):
    """
    A field that accepts characters only from an alphabet of allowed
    characters. A set of allowed punctuation characters are allowed and
    discarded when cleaned.
    """
    required_types = (str)
    type_name = u'string'

    alphabet = None
    punctuation = None

    min_length = 0
    max_length = float('inf')

    default_error_messages = {
        "allowed_characters": _("Only the characters '{alphabet}{punctuation}' are allowed"),
        "min_length": "Minimum length {0}",
        "max_length": "Maximum length {0}",
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
            raise ValidationException(
                self.error_messages['allowed_characters'].format(
                    alphabet=self.alphabet,
                    punctuation=self.punctuation))

        if len(value) < self.min_length:
            raise ValidationException(
                self.error_messages['min_length'].format(self.min_length))

        if len(value) > self.max_length:
            raise ValidationException(
                self.error_messages['max_length'].format(self.max_length))

        return value

    def __copy__(self, **kwargs):
        return super(PunctuatedCharacterField, self).__copy__(
            alphabet=self.alphabet, punctuation=self.punctuation,
            min_length=self.min_length, max_length=self.max_length)


class RestrictedCharacterField(PunctuatedCharacterField):
    """
    A field that only allows a defined alphabet of characters to be used
    """
    punctuation = ''


class DigitField(RestrictedCharacterField):
    """
    A field that only allows digits. It is not treated as a number, however,
    and leading zeros are preserved
    """
    alphabet = '0123456789'


class CreditCardField(PunctuatedCharacterField):
    """
    Accepts credit card numbers
    """
    punctuation = ' -'
    alphabet = '0123456789'

    min_length = 12
    max_length = 20

    default_error_messages = {
        "luhn_checksum": _("The credit card number is not valid"),
    }

    def clean(self, data):
        value = super(CreditCardField, self).clean(data)

        if not self.luhn_checksum(value):
            raise ValidationException(self.error_messages['luhn_checksum'])

        return value

    def luhn_checksum(self, card_number):
        digits = list(map(int, reversed(card_number)))
        evens = sum(digits[0::2])
        odds = sum(sum(divmod(digit * 2, 10)) for digit in digits[1::2])
        return (evens + odds) % 10 == 0


class ListField(TypedField):
    """
    List fields allow checking that all items in a list all pass
    validation.
    """

    required_types = list
    type_name = 'list'

    def __init__(self, field, **kwargs):
        """
        Construct a new ListField

        In addition to the arguments accepted by the ``Field`` class, the
        following arguments are accepted:

        * ``field`` should be an instance of a Field subclass. Each item in the
          submitted list will be validated and cleaned with Field.
        """
        super(ListField, self).__init__(**kwargs)
        self.field = field

    def clean(self, data):
        value = super(ListField, self).clean(data)

        errors = InvalidDataException()
        cleaned_list = []
        for i, datum in enumerate(value):
            try:
                cleaned_list.append(self.field.clean(datum))
            except BaseValidationException as err:
                errors.invalid_fields[i] = err

        if errors:
            raise errors
        return cleaned_list


class NestedValidator(TypedField):
    """
    Nested validators allow nesting dicts inside one another. A validator is
    used to validate and clean the nested dict.
    """
    required_types = (dict, )
    type_name = 'object'

    def __init__(self, validator, **kwargs):
        """
        Construct a new NestedValidator

        In addition to the arguments accepted by the ``Field`` class, the
        following arguments are accepted:

        * ``validator`` should be an instance of a Validator class. The nested
          dict is passed to this validator for validation and cleaning.
        """
        super(NestedValidator, self).__init__(**kwargs)
        self.validator = validator

    def clean(self, data):
        value = super(NestedValidator, self).clean(data)
        return self.validator.clean(value)

    def __copy__(self, **kwargs):
        return super(NestedValidator, self).__copy__(validator=self.validator)

import datetime

from valedictory import Validator
from valedictory.exceptions import (
    InvalidDataException, NoData, ValidationException)
from valedictory.fields import (
    BooleanField, ChoiceField, ChoiceMapField, CreditCardField, DateField,
    DateTimeField, DigitField, EmailField, Field, IntegerField, ListField,
    NestedValidator, StringField, YearMonthField)

from .utils import ValidatorTestCase


class TestField(ValidatorTestCase):

    def test_required(self):
        field = Field()
        self.assertEqual("hello", field.clean("hello"))
        self.assertEqual("", field.clean(""))

        with self.assertRaises(ValidationException):
            field.clean(NoData)

    def test_not_required(self):
        field = StringField(required=False)
        self.assertEqual("hello", field.clean("hello"))
        self.assertEqual("", field.clean(""))

        with self.assertRaises(NoData):
            field.clean(NoData)


class TestStringField(ValidatorTestCase):

    def test_simple(self):
        field = StringField()
        self.assertEqual("hello", field.clean("hello"))
        with self.assertRaises(ValidationException):
            self.assertEqual("", field.clean(""))

    def test_min_length(self):
        field = StringField(min_length=3)

        self.assertEqual("hello", field.clean("hello"))
        with self.assertRaises(ValidationException):
            field.clean("no")

    def test_max_length(self):
        field = StringField(max_length=3)

        self.assertEqual("hi", field.clean("hi"))
        with self.assertRaises(ValidationException):
            field.clean("hello")

    def test_not_required(self):
        field = StringField(required=False)
        self.assertEqual("", field.clean(""))
        with self.assertRaises(NoData):
            field.clean(NoData)

    def test_invalid_type(self):
        field = StringField()
        with self.assertRaises(ValidationException):
            field.clean(10)


class TestBooleanField(ValidatorTestCase):

    def test_simple(self):
        field = BooleanField()
        self.assertEqual(True, field.clean(True))
        self.assertEqual(False, field.clean(False))

    def test_invalid_type(self):
        field = BooleanField()
        with self.assertRaises(ValidationException):
            field.clean(0)
        with self.assertRaises(ValidationException):
            field.clean(1)
        with self.assertRaises(ValidationException):
            field.clean("")
        with self.assertRaises(ValidationException):
            field.clean("True")
        with self.assertRaises(ValidationException):
            field.clean("true")


class TestIntegerField(ValidatorTestCase):

    def test_simple(self):
        field = IntegerField()
        self.assertEqual(-10, field.clean(-10))
        self.assertEqual(0, field.clean(0))
        self.assertEqual(42, field.clean(42))

    def test_floats(self):
        field = IntegerField()
        with self.assertRaises(ValidationException):
            field.clean(1.0)
        with self.assertRaises(ValidationException):
            field.clean(3.14159264)

    def test_invalid_type(self):
        field = IntegerField()
        with self.assertRaises(ValidationException):
            field.clean("Hello")
        with self.assertRaises(ValidationException):
            field.clean("10")
        with self.assertRaises(ValidationException):
            field.clean(True)


class TestEmailField(ValidatorTestCase):

    def test_simple(self):
        field = EmailField()
        self.assertEqual("test@example.com", field.clean("test@example.com"))
        # Address validation is not perfect...
        self.assertEqual("t@e.c", field.clean("t@e.c"))

    def test_max_length(self):
        field = EmailField(max_length=10)
        self.assertEqual("t@e.c", field.clean("t@e.c"))
        with self.assertRaises(ValidationException):
            field.clean("test@example.com")

    def test_invalid_address(self):
        field = EmailField()
        with self.assertRaises(ValidationException):
            field.clean("t@e")
        with self.assertRaises(ValidationException):
            field.clean("@te.com")
        with self.assertRaises(ValidationException):
            field.clean("test@")
        with self.assertRaises(ValidationException):
            field.clean("te.com")
        with self.assertRaises(ValidationException):
            field.clean("test")

    def test_invalid_type(self):
        field = EmailField()
        with self.assertRaises(ValidationException):
            field.clean(10)


class TestDateTimeField(ValidatorTestCase):

    def test_simple(self):
        field = DateTimeField()
        # This uses the iso8601 library directly, which has its own tests.
        # Assuming its tests are good, we dont need to do much.
        self.assertEqual(
            datetime.datetime(1989, 10, 16, 8, 23, 45, tzinfo=datetime.timezone.utc),
            field.clean("1989-10-16T08:23:45"))

        self.assertEqual(
            datetime.datetime(1989, 10, 16, 8, 23, 45, tzinfo=datetime.timezone.utc),
            field.clean("1989-10-16 08:23:45Z"))

        self.assertEqual(
            datetime.datetime(1989, 10, 16, 8, 23, 45, tzinfo=datetime.timezone.utc),
            field.clean("19891016T082345+0000"))

    def test_invalid_dates(self):
        field = DateTimeField()

        # No leap year this year
        with self.assertRaises(ValidationException):
            field.clean("2015-02-29T10:11:12")

        # wat r u doin?
        with self.assertRaises(ValidationException):
            field.clean("Not even a date")


class TestDateField(ValidatorTestCase):

    def test_simple(self):
        field = DateField()
        self.assertEqual(
            datetime.date(1989, 10, 16),
            field.clean("1989-10-16"))
        self.assertEqual(
            datetime.date(1989, 10, 16),
            field.clean("19891016"))
        self.assertEqual(
            datetime.date(2345, 6, 7),
            field.clean("2345-6-7"))

    def test_invalid_dates(self):
        field = DateField()

        # No leap year this year
        with self.assertRaises(ValidationException):
            field.clean("2015-2-29")

        # Too many numbers in the year.
        # Sorry, Long Now Foundation!
        with self.assertRaises(ValidationException):
            field.clean("10000-01-01")

        # Small dates dont work either. Anything before 1582 is a bit suss in
        # the Gregorian calendar anyway.
        with self.assertRaises(ValidationException):
            field.clean("999-01-01")

        # wat r u doin?
        with self.assertRaises(ValidationException):
            field.clean("Not even a date")

    def test_different_formats(self):
        field = DateField(formats=['%d/%m/%Y'])
        self.assertEqual(
            datetime.date(2345, 6, 7),
            field.clean("7/6/2345"))
        with self.assertRaises(ValidationException):
            field.clean('2345-06-07')


class TestYearMonthField(ValidatorTestCase):

    def test_simple(self):
        field = YearMonthField()
        self.assertEqual(
            (1989, 10),
            field.clean("1989-10"))
        self.assertEqual(
            (2345, 6),
            field.clean("2345-06"))

    def test_invalid_dates(self):
        field = EmailField(max_length=10)

        # Too many numbers in the year.
        # Sorry, Long Now Foundation!
        with self.assertRaises(ValidationException):
            field.clean("10000-01")

        # Small dates dont work either. Sorry.
        with self.assertRaises(ValidationException):
            field.clean("999-01")

        # wat r u doin?
        with self.assertRaises(ValidationException):
            field.clean("nope-no")


class TestChoiceField(ValidatorTestCase):

    def test_simple(self):
        choices = ["hello", 10, True, False, None]
        field = ChoiceField(choices)
        for choice in choices:
            self.assertEqual(
                choice,
                field.clean(choice))

    def test_invalid(self):
        choices = ["hello", 10, True, False, None]
        invalid_choices = ["nope", 11, {}, []]
        field = ChoiceField(choices)
        for choice in invalid_choices:
            with self.assertRaises(ValidationException):
                field.clean(choice)


class TestChoiceMapField(ValidatorTestCase):

    def test_simple(self):
        choices = {"foo": "bar", 1: 2, True: False, None: {"hello": "world"}}
        field = ChoiceMapField(choices)
        for data, cleaned_data in choices.items():
            self.assertEqual(
                cleaned_data,
                field.clean(data))

    def test_invalid(self):
        choices = {"foo": "bar", 1: 2, True: False, None: {"hello": "world"}}
        invalid_choices = ["nope", 11, {}, []]
        field = ChoiceMapField(choices)
        for choice in invalid_choices:
            with self.assertRaises(ValidationException):
                field.clean(choice)


class TestDigitField(ValidatorTestCase):

    def test_simple(self):
        field = DigitField()
        self.assertEqual(
            "1234567890",
            field.clean("1234567890"))
        self.assertEqual(
            "000",
            field.clean("000"))
        self.assertEqual(
            "01020",
            field.clean("01020"))

    def test_invalid(self):
        field = DigitField()
        with self.assertRaises(ValidationException):
            field.clean("hello")
        with self.assertRaises(ValidationException):
            field.clean("123abc")
        with self.assertRaises(ValidationException):
            field.clean("abc123")


class TestCreditCardField(ValidatorTestCase):

    def test_simple(self):
        field = CreditCardField()
        self.assertEqual(
            "5123456789012346",
            field.clean("5123 4567 8901 2346"))
        self.assertEqual(
            "4111111111111111",
            field.clean("4111-1111-1111-1111"))
        self.assertEqual(
            "378282246310005",
            field.clean("3 78 2-82 2--46  3 -10- 005"))

    def test_invalid_numbers(self):
        field = CreditCardField()
        with self.assertRaises(ValidationException):
            field.clean('5123_4567_8901_2346')
        with self.assertRaises(ValidationException):
            field.clean('5111111111111111')


class TestListField(ValidatorTestCase):
    def test_string_list(self):
        field = ListField(StringField())

        self.assertEqual(
            ["foo", "bar", "baz"],
            field.clean(["foo", "bar", "baz"]))

        self.assertEqual([], field.clean([]))

    def test_int_list(self):
        field = ListField(IntegerField())

        self.assertEqual(
            [1, 2, 3, 4],
            field.clean([1, 2, 3, 4]))

        self.assertEqual([], field.clean([]))

    def test_bad_list(self):
        """
        Errors should be indexed by their index in the list
        """
        field = ListField(IntegerField())

        try:
            field.clean([1, "nope", 3, "strings"])
        except InvalidDataException as e:
            self.assertEqual([1, 3], sorted(e.invalid_fields.keys()))
        else:
            self.fail("Expecting to catch ValidationException")


class TestNestedValidators(ValidatorTestCase):
    def test_nested_validator(self):
        field = NestedValidator(Validator(fields={
            'int': IntegerField(),
            'string': StringField()}))

        self.assertEqual(
            {'int': 10, 'string': 'foo'},
            field.clean({'string': 'foo', 'int': 10}))


class TestNestedLists(ValidatorTestCase):
    def test_nested_lists(self):
        field = ListField(NestedValidator(Validator(fields={
            'int': IntegerField(), 'string': StringField()})))

        data = [{'int': i, 'string': s}
                for i, s in zip(range(3), 'foo bar baz'.split())]
        self.assertEqual(
            data,
            field.clean(data))

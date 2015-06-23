import unittest

from valedictory import Validator, fields
from valedictory.base import partition_dict


class TestValidators(unittest.TestCase):

    def test_cleaning_fields(self):
        validator = Validator(fields={
            'int': fields.IntegerField(),
            'string': fields.StringField()})

        data = {'int': 10, 'string': 'foo'}
        cleaned_data, errors = validator.clean(data)

        self.assertEqual(data, cleaned_data)
        self.assertIsNone(errors)

    def test_unknown_fields_disallowed(self):
        """
        Unknown fields should throw an error
        """
        validator = Validator(fields={
            'int': fields.IntegerField(),
            'string': fields.StringField()})

        data = {'int': 10, 'string': 'foo', 'nope': 'nope'}
        cleaned_data, errors = validator.clean(data)
        self.assertEqual(['nope'], sorted(errors.keys()))
        self.assertIsNone(cleaned_data)

    def test_unknown_fields_allowed(self):
        """
        Unknown fields can be silently allowed by setting a flag
        """
        validator = Validator(allow_unknown_fields=True, fields={
            'int': fields.IntegerField(),
            'string': fields.StringField()})

        cleaned_data, errors = validator.clean({'int': 10, 'string': 'foo', 'nope': 'nope'})

        self.assertEqual({'int': 10, 'string': 'foo'}, cleaned_data)
        self.assertIsNone(errors)


class TestDeclarativeValidators(unittest.TestCase):

    def test_no_inheritance(self):
        class MyValidator(Validator):
            int = fields.IntegerField()
            string = fields.StringField()

        self.assertEqual(
            sorted(MyValidator.fields.keys()),
            ['int', 'string'])

        data = {'int': 10, 'string': 'foo'}
        cleaned_data, errors = MyValidator().clean(data)
        self.assertEqual(data, cleaned_data)
        self.assertIsNone(errors)

    def test_single_inheritance(self):
        class ParentValidator(Validator):
            int = fields.IntegerField()

        class ChildValidator(ParentValidator):
            string = fields.StringField()

        self.assertEqual(
            sorted(ChildValidator.fields.keys()),
            ['int', 'string'])

    def test_multiple_inheritance(self):
        class P1Validator(Validator):
            int = fields.IntegerField()
            override = fields.BooleanField()

        class P2Validator(Validator):
            string = fields.StringField()
            override = fields.DateField()

        class ChildValidator(P1Validator, P2Validator):
            email = fields.EmailField()

        self.assertEqual(
            sorted(ChildValidator.fields.keys()),
            sorted(['email', 'int', 'override', 'string']))

        # Field overriding should occur in MRO order, so override should have
        # come from P1Validator
        self.assertIsInstance(ChildValidator.fields['override'],
                              fields.BooleanField)

    def test_methods_and_attributes(self):
        class MyValidator(Validator):
            int = fields.IntegerField()
            string = fields.StringField()

            bar = "baz"

            def do_thing(self):
                return "foo"

        self.assertEqual(
            sorted(MyValidator.fields.keys()),
            ['int', 'string'])

        validator = MyValidator()
        data = {'int': 10, 'string': 'foo'}
        cleaned_data, errors = validator.clean(data)

        self.assertEqual(data, cleaned_data)
        self.assertIsNone(errors)
        self.assertEqual("foo", validator.do_thing())
        self.assertEqual("baz", validator.bar)


class TestMisc(unittest.TestCase):
    def test_partition_dict(self):
        keys = set()
        values = set()

        def pred(key, value):
            keys.add(key)
            values.add(value)
            return key % 2 == 0

        d = {i: chr(i + 65) for i in range(10)}
        odd, even = partition_dict(d, pred)

        self.assertEqual(odd, {1: 'B', 3: 'D', 5: 'F', 7: 'H', 9: 'J'})
        self.assertEqual(even, {0: 'A', 2: 'C', 4: 'E', 6: 'G', 8: 'I'})
        self.assertEqual(keys, set(range(10)))
        self.assertEqual(values, set("ABCDEFGHIJ"))

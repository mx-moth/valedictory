from valedictory import Validator, fields
from valedictory.exceptions import (
    InvalidDataException, ValidationException)

from .utils import ValidatorTestCase


class TestInvalidDataException(ValidatorTestCase):
    def test_simple_errors(self):
        validator = Validator(fields={
            'int': fields.IntegerField(), 'string': fields.StringField()})
        with self.assertRaises(InvalidDataException) as cm:
            validator.clean({'int': 'nope', 'unknown': 'nope'})
        errors = cm.exception

        expected_errors = InvalidDataException({
            'int': [ValidationException('This field must be a integer')],
            'string': [ValidationException('This field is required')],
            'unknown': [ValidationException('Unknown field')]})
        self.assertEqual(errors, expected_errors)

    def test_nested_errors(self):

        validator = Validator(fields={
            'name': fields.StringField(min_length=1),
            'items': fields.ListField(fields.NestedValidator(Validator({
                'code': fields.StringField(min_length=6, max_length=6),
                'quantity': fields.IntegerField(min=1),
            }))),
        })

        with self.assertRaises(InvalidDataException) as cm:
            validator.clean({
                'name': '',
                'items': [
                    {'code': 'ABC123', 'quantity': 1},
                    'not a dict',
                    {'code': 'A1', 'quantity': 0},
                    {'code': 'BCD234', 'quantity': 2, 'unknown': 'wat'},
                ]
            })
        errors = cm.exception

        self.assertEqual(errors, InvalidDataException({
            'name': [ValidationException('This field is required')],
            'items': [InvalidDataException({
                1: [ValidationException('This field must be a object')],
                2: [InvalidDataException({
                    'code': [ValidationException('Minimum length 6')],
                    'quantity': [ValidationException('This must be equal to or greater than the minimum of 1')],
                })],
                3: [InvalidDataException({
                    'unknown': [ValidationException('Unknown field')],
                })],
            })],
        }))


class TestFlatten(ValidatorTestCase):
    def test_one_level(self):
        errors = InvalidDataException({
            'foo': [ValidationException("foo error")],
            'bar': [
                ValidationException("bar error 1"),
                ValidationException("bar error 2"),
            ],
        })

        self.assertEqual(set(errors.flatten()), set([
            (('bar',), 'bar error 1'),
            (('bar',), 'bar error 2'),
            (('foo',), 'foo error')]))

    def test_nested_dict_errors(self):
        errors = InvalidDataException({
            'foo': [ValidationException("foo error")],
            'bar': [InvalidDataException({
                'baz': [
                    ValidationException("bar baz error 1"),
                    ValidationException("bar baz error 2"),
                ],
                'quux': [ValidationException("bar quux error")],
            })],
        })

        self.assertEqual(set(errors.flatten()), set([
            (('bar', 'baz'), 'bar baz error 1'),
            (('bar', 'baz'), 'bar baz error 2'),
            (('bar', 'quux'), 'bar quux error'),
            (('foo',), 'foo error')]))

    def test_nested_list_errors(self):
        errors = InvalidDataException({
            'foo': [ValidationException("foo error")],
            'bar': [InvalidDataException({
                1: [ValidationException("bar 1 error")],
                3: [ValidationException("bar 3 error")],
            })],
        })

        self.assertEqual(set(errors.flatten()), set([
            (('bar', 1), 'bar 1 error'),
            (('bar', 3), 'bar 3 error'),
            (('foo',), 'foo error')]))

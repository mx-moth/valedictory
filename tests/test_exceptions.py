import unittest

from valedictory.exceptions import (
    ValidationErrors, ValidationException, NestedValidatorException)


class TestExceptions(unittest.TestCase):
    def test_one_level(self):
        errors = ValidationErrors({
            'foo': [ValidationException("foo error")],
            'bar': [
                ValidationException("bar error 1"),
                ValidationException("bar error 2"),
            ],
        })

        self.assertEqual(list(errors.flatten()), [
            (['bar'], ['bar error 1', 'bar error 2']),
            (['foo'], ['foo error'])])

    def test_nested_dict_errors(self):
        errors = ValidationErrors({
            'foo': [ValidationException("foo error")],
            'bar': NestedValidatorException(ValidationErrors({
                'baz': [ValidationException("bar baz error")],
                'quux': [ValidationException("bar quux error")],
            })),
        })

        self.assertEqual(list(errors.flatten()), [
            (['bar', 'baz'], ['bar baz error']),
            (['bar', 'quux'], ['bar quux error']),
            (['foo'], ['foo error'])])

    def test_nested_list_rrors(self):
        errors = ValidationErrors({
            'foo': [ValidationException("foo error")],
            'bar': NestedValidatorException(ValidationErrors({
                1: [ValidationException("bar 1 error")],
                3: [ValidationException("bar 3 error")],
            })),
        })

        self.assertEqual(list(errors.flatten()), [
            (['bar', 1], ['bar 1 error']),
            (['bar', 3], ['bar 3 error']),
            (['foo'], ['foo error'])])

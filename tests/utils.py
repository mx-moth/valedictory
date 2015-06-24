import unittest
from valedictory.exceptions import InvalidDataException


class ValidatorTestCase(unittest.TestCase):
    maxDiff = 2000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addTypeEqualityFunc(InvalidDataException, 'assertInvalidDataExceptionEqual')

    def assertInvalidDataExceptionEqual(self, left, right, msg=None):
        return self.assertDictEqual(
            left.invalid_fields, right.invalid_fields, msg=msg)

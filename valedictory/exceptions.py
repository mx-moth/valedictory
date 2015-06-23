from __future__ import absolute_import, unicode_literals

from collections import defaultdict


class ValidationErrors(defaultdict):
    """
    Lists of validation errors for each field in a validator.

    Only filled out for a field if the field has an error.
    """
    def __init__(self, errors={}):
        super(ValidationErrors, self).__init__(list)
        self.update(errors)

    def __repr__(self):
        inner = ', '.join('{0}: {1}'.format(k, v) for k, v in self.items())
        return '{' + inner + '}'

    def flatten(self):
        """
        Yield a pair of ``(path, errors)`` for each error.

        >>> list(errors.flatten())
        [
            (['bar'], ['Unknown field']),
            (['foo'], ['This field can not be empty']),
        ]

        If an error is a :cls:`NestedValidatorException`, then errors are
        recursively extracted.  ``path`` will be an array of the path to the
        error. ``errors`` will be an array of the error messages from these
        errors.

        If validator was constructed for a shopping card, which had user
        details and a list of items in a shopping cart, made using a
        NestedValidator inside a ListField, some possible flattened errors
        might be:

        >>> list(errors.flatten())
        [
            (['name'], ['This field can not be empty']),
            (['items', 2, 'quantity'], ['This must be equal to or greater than the minimum of 1']),
        ]
        """
        for name, error_list in sorted(self.items()):
            if isinstance(error_list, NestedValidatorException):
                for nested_name, error in error_list.errors.flatten():
                    yield [name] + nested_name, error
            else:
                yield [name], [error.msg for error in error_list]


class BaseValidationException(Exception):
    """
    All exceptions used by this will be subclasses of this exception class.
    """
    pass


class ValidationException(BaseValidationException):
    """
    Something is wrong!
    """
    def __init__(self, message, **kwargs):
        self.msg = message
        super(ValidationException, self).__init__(message, **kwargs)

    def __str__(self):
        return '{cls}: {msg}'.format(cls=self.__class__.__name__,
                                     msg=self.msg)

    def __repr__(self):
        return '<{str}>'.format(str=self)


class NestedValidatorException(BaseValidationException):
    """
    Something is wrong! Specifically in a nested validator.
    """
    def __init__(self, errors):
        self.errors = errors


class NoData(BaseValidationException):
    """
    Used to indicate that this field had no data supplied. This is different
    from having empty data, which is represented by ``None``. This bypasses the
    bit where data is set in the output dict, so the output dict will **not**
    have the associated key.
    """
    pass

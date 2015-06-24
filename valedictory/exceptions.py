from __future__ import absolute_import, unicode_literals


class BaseValidationException(Exception):
    """
    All exceptions used by this will be subclasses of this exception class.
    """
    pass


class InvalidDataException(BaseValidationException):
    """
    Lists of validation errors for each field in a validator.

    Only filled out for a field if the field has an error.
    """
    def __init__(self, errors={}):
        super(BaseValidationException, self).__init__()
        self.invalid_fields = {}
        self.invalid_fields.update(errors)

    def __str__(self):
        inner = ', '.join('{0}: {1}'.format(k, v)
                          for k, v in self.invalid_fields.items())
        return '{' + inner + '}'

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, str(self))

    def __bool__(self):
        return bool(self.invalid_fields)

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
        for name, error in self.invalid_fields.items():
            if isinstance(error, InvalidDataException):
                for nested_name, nested_error in error.flatten():
                    yield (name,) + nested_name, nested_error
            else:
                yield (name,), error.msg

    def __eq__(self, other):
        if not isinstance(other, InvalidDataException):
            return NotImplemented
        return self.invalid_fields == other.invalid_fields


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

    def __eq__(self, other):
        if not isinstance(other, ValidationException):
            return NotImplemented
        return self.msg == other.msg


class NoData(BaseValidationException):
    """
    Used to indicate that this field had no data supplied. This is different
    from having empty data, which is represented by ``None``. This bypasses the
    bit where data is set in the output dict, so the output dict will **not**
    have the associated key.
    """
    pass

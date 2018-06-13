from collections import defaultdict


class BaseValidationException(Exception):
    """
    All validation exceptions will be subclasses of this exception.
    """
    pass


class InvalidDataException(BaseValidationException):
    """
    Lists of validation errors for each field in a validator.

    Only filled out for a field if the field has an error.

    .. autoattribute:: invalid_fields
        :annotation:

    .. automethod:: flatten
    """

    #: A dict with the validation exceptions for all fields that
    #: failed validation.
    #: Normal field errors will be a
    #: :exc:`~valedictory.exceptions.ValidationException` instance,
    #: while errors for
    #: :class:`~valedictory.fields.ListField` and
    #: :class:`~valedictory.fields.NestedValidator`
    #: may also be :exc:`InvalidDataException` instances.
    invalid_fields = None

    def __init__(self, errors={}):
        super(BaseValidationException, self).__init__()
        self.invalid_fields = defaultdict(list)
        self.invalid_fields.update(errors)

    def __str__(self):
        inner = ', '.join('{0}: {1}'.format(k, v)
                          for k, v in self.invalid_fields.items())
        return '{' + inner + '}'

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, str(self))

    def __bool__(self):
        return bool(self.invalid_fields)

    def __eq__(self, other):
        if not isinstance(other, InvalidDataException):
            return NotImplemented
        return self.invalid_fields == other.invalid_fields

    def __hash__(self):
        return id(self)

    def flatten(self):
        """
        Yield a pair of ``(path, errors)`` for each error.

        >>> list(errors.flatten())
        [
            (['bar'], ['Unknown field']),
            (['foo'], ['This field can not be empty']),
        ]

        If an error is a :class:`InvalidDataException`, then errors are
        recursively extracted.  ``path`` will be an array of the path to the
        error. ``errors`` will be an array of the error messages from these
        errors.

        If validator was constructed for a shopping cart, which had user
        details and a list of items in a shopping cart,
        made using a :class:`~valedictory.fields.NestedValidator`
        inside a :class:`~valedictory.fields.ListField`,
        some possible flattened errors might be:

        >>> list(errors.flatten())
        [
            (['name'], ['This field can not be empty']),
            (['items', 2, 'quantity'], ['This must be equal to or greater than the minimum of 1']),
        ]
        """
        for name, error_list in self.invalid_fields.items():
            for error in error_list:
                if isinstance(error, InvalidDataException):
                    for nested_name, nested_error in error.flatten():
                        yield (name,) + nested_name, nested_error
                else:
                    yield (name,), error.msg


class ValidationException(BaseValidationException):
    """
    A field has failed validation.

    .. autoattribute:: msg
        :annotation:

    .. autoattribute:: code
        :annotation:
    """

    #: The validation error as a human readable string. This error is
    #: translatable via gettext, and should not be used for checking the type
    #: of error
    msg = None

    #: The validation error code as a string. This can be used to check the
    #: type of error
    code = None

    def __init__(self, message, code, **kwargs):
        self.msg = message
        self.code = code
        super(ValidationException, self).__init__(message, **kwargs)

    def __str__(self):
        return self.msg

    def __repr__(self):
        return '<{cls}: ({code}) {msg}>'.format(
            cls=type(self).__name__, code=self.code, msg=self.msg)

    def __eq__(self, other):
        if not isinstance(other, ValidationException):
            return NotImplemented
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)


class NoData(BaseValidationException):
    """
    Used to indicate that this field had no data supplied. This is different
    from having empty data, which is represented by ``None``. This bypasses the
    bit where data is set in the output dict, so the output dict will **not**
    have the associated key.
    """
    def __str__(self):
        return self.__class__.__name__

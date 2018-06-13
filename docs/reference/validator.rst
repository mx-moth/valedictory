.. _validator:

.. module:: valedictory

Validator
=========

.. autoclass:: Validator

    The base class from which all custom validators are created.
    To define a resuable custom validator,
    create a new subclass of :class:`Validator`
    and add any fields required:

    .. code:: python

        from valedictory import Validator, fields

        class ContactValidator(Validator):
            allow_unknown_fields = True

            default_error_messages = {
                'unknown': "I don't know what this field is"
            }

            name = fields.CharField()
            height = fields.IntegerField()
            date_of_birth = fields.DateField()

        contact_validator = ContactValidator()

    Alternatively, a validator can be defined by instantiating :class:`Validator`:

    .. code:: python

        contact_validator = Validator(
            allow_unknown_fields = True,
            error_messages = {
                'unknown': "I don't know what this field is"
            },
            fields={
                'name': fields.CharField(),
                'height': fields.IntegerField(),
                'date_of_birth': fields.DateField()
            },
        )

    This is useful for one-off validators,
    or with a :class:`~valedictory.fields.NestedValidator`.

    **Attributes**

    .. autoattribute:: allow_unknown_fields

        Whether unknown fields in the data should be treated as an error, or ignored.
        If ``allow_unknown_fields`` is ``True``,
        fields in the data being cleaned that do not have a corresponding field on the class
        cause a :exc:`~valedictory.exceptions.InvalidDataException` to be thrown

        The default is ``False``, unknown fields are not allowed.

    .. autoattribute:: fields
        :annotation: = {name: Field()}

        A dictionary of all the fields on this validator

    .. autoattribute:: default_error_messages
        :annotation: = {'error': "Error message"}

        A dictionary of strings for each error message that can be thrown.
        You can override error messages by overriding this dictionary.
        Only the error messages being overridden need to be set,
        other error messages will be taken from the parent classes.

        unknown
            Thrown when an unknown key is present in the data being validated
            and :attr:`allow_unknown_fields` is ``True``.

    **Methods**

    .. automethod:: clean
    .. automethod:: error

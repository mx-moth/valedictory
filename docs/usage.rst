.. _usage:

=====
Usage
=====

All validation is done by :class:`~valedictory.Validator` subclasses,
and the fields from :mod:`valedictory.fields`.
The schema to validate data against is defined declaratively
by subclassing :class:`~valedictory.Validator`:

.. code:: python

    from valedictory import Validator, fields

    class ContactValidator(Validator):
        name = fields.CharField()
        height = fields.IntegerField()
        date_of_birth = fields.DateField()

:class:`~valedictory.Validator` instances are immutable,
so the same instance can be reused to validate all your data.

.. code:: python

    contact_validator = ContactValidator()

Validation is done by calling the :meth:`~valedictory.Validator.clean` method
on a :class:`~valedictory.Validator` instance.
:meth:`~valedictory.Validator.clean` will either returned the cleaned data,
or raise an :exc:`~valedictory.exceptions.InvalidDataException`.
:exc:`~valedictory.exceptions.InvalidDataException` instances
store all the validation errors found when validating the data.
These can be used to create an appropriate error response.

.. code:: python

    from valedictory.exceptions import InvalidDataException

    input_data = json.loads(request.body)

    try:
        cleaned_data = contact_validator.clean(input_data)

        # Save the data
        Contact.objects.create(**cleaned_data)

    except InvalidDataException as errors:
        # Handle the error
        for path, message in errors.flatten():
            print("{0}: {1}".format('.'.join(path), message))

==========================================
Valedictory - validate Python dictionaries
==========================================

Declare a schema, then validate Python dictionaries against it:

.. code:: python

    from valedictory import Validator, fields, InvalidDataException

    class ContactValidator(Validator):
        name = fields.CharField()
        height = fields.IntegerField()
        date_of_birth = fields.DateField()

    contact_validator = ContactValidator()

    input_data = json.loads(request.body)

    try:
        cleaned_data = contact_validator.clean(input_data)

        # Save the data
        Contact.objects.create(**cleaned_data)

    except InvalidDataException as errors:
        # Handle the error
        for path, message in errors.flatten():
            print("{0}: {1}".format('.'.join(path), message))

Documentation
=============

.. toctree::
    :maxdepth: 2

    setup
    usage
    reference/index



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


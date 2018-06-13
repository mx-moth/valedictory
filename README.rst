===========
valedictory
===========

.. image:: https://badge.fury.io/py/valedictory.svg
    :target: https://pypi.org/project/valedictory/
.. image:: https://readthedocs.org/projects/valedictory/badge/?version=latest
    :target: https://valedictory.readthedocs.io/en/latest/

Valedictory validates the data in ``dict``\s.
It is designed for use in API validation,
and other situations where you are receiving structured JSON data
as opposed to key-value POST form data.
It takes in a dict of data (probably obtained from a JSON POST request),
and validates that data against some fields.

Validators are defined as classes.
Declare fields on a Validator class.
Once constructed, Validator instances are immutable.

.. code-block:: python

    from valedictory import Validator, fields, InvalidDataException

    class PersonValidator(Validator):
        name = fields.CharField()
        height = fields.IntegerField()
        date_of_birth = fields.DateField()

    person_validator = PersonValidator()

A Python dict can be checked to see if it conforms to this validator.
The dict can come from a JSON POST request, or a configuration file,
or any other external data source that needs validation and cleaning.
The cleaned data will be returned.
Validator classes will return a dict of cleaned data.
Each field type may transform the data as part of cleaning it.
For example, the ``DateField`` will transform the data
into a ``datetime.date`` instance.

.. code-block:: python

    input_data = json.loads(request.body)

    try:
        # cleaned_data will be a dict of cleaned, validated data
        cleaned_data = person_validator.clean(input_data)

        # Do something with the returned data
        Person.objects.create(**cleaned_data)

    except InvalidDataException as errors:
        # The data did not pass validation
        for path, message in errors.flatten():
            # This will print something like 'name: This field is required'
            print("{0}: {1}".format('.'.join(path), message))

Validators can be nested, allowing dicts of arbitrary complexity:

.. code-block:: python

    class ArticleValidator(Validator):
        content = fields.CharField()
        published = fields.DateTimeField()
        author = fields.NestedValidator(PersonValidator())
        tags = fields.ListField(fields.CharField())

    # Some example data that would pass validation:
    data = {
        "content": "An interesting article",
        "published": "2018-06-13T1:44:00+10:00",
        "author": {
            "name": "Alex Smith",
            "height": 175,
            "date_of_birth": "1990-03-26",
        },
        "tags": ["humour", "interesting", "clickbait"],
    }

`Read the documentation for more information <https://valedictory.readthedocs.io>`_.

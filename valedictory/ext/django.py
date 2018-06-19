"""
Fields that integrate with Django.
"""

import copy

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.core.validators import URLValidator
from django.db.models import Model
from django.utils.translation import ugettext_lazy as _

from valedictory import fields


class UploadedFileField(fields.TypedField):
    """
    Accepts uploaded files
    """
    required_types = UploadedFile
    type_name = 'file'


class ForeignKeyField(fields.TypedField):
    """
    Accepts foreign keys to a Django model, and returns the model instance when
    cleaned.

    .. autoattribute:: default_error_messages
        :annotation:
    """
    type_name = 'foreign key'

    default_error_messages = {
        'missing': _("Object does not exist"),
        'multiple': _("Multiple objects returned"),
    }

    def __init__(self, queryset, field='pk', key_type=int, **kwargs):
        super(ForeignKeyField, self).__init__(**kwargs)
        """
        Construct a new ForeignKeyField

        In addition to the arguments accepted by the ``Field`` class, the
        following arguments are accepted:

        * The models that the field can reference is set by ``queryset``.
          If a model is supplied, all objects of that type are allowed.
        * ``field`` is the name of the model field to search on. Defaults to
          ``pk``.
        * ``key_type`` is the type of the field being searched. Defaults to
          ``int``
        """
        if isinstance(queryset, Model):
            queryset = queryset.objects.all()
        self.queryset = queryset
        self.field = field
        self.required_types = key_type

    def clean(self, value):
        value = super().clean(value)
        queryset = self.queryset
        model = queryset.model
        try:
            return queryset.get(**{self.field: value})
        except model.DoesNotExist:
            raise self.error('missing')
        except model.MultipleObjectsReturned:
            raise self.error('multiple')

    def __deepcopy__(self, memo):
        obj = super(ForeignKeyField, self).__deepcopy__(memo)
        obj.queryset = copy.deepcopy(obj.queryset, memo)
        return obj


class URLField(fields.StringField):
    """
    Accepts a URL as a string.
    """
    validator = URLValidator()
    default_error_messages = {
        'invalid_url': _("Invalid URL"),
    }

    def clean(self, value):
        value = super().clean(value)
        try:
            self.validator(value)
        except ValidationError:
            raise self.error('invalid_url')
        return value

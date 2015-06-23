from __future__ import absolute_import, unicode_literals

from django.core.files.uploadedfile import UploadedFile
from django.db.models import Model

from valedictory.exceptions import ValidationException
from valedictory.fields import TypedField


class UploadedFileField(TypedField):
    """
    Accepts uploaded files
    """
    required_types = UploadedFile
    type_name = 'file'


class ForeignKeyField(TypedField):
    """
    A field that accepts foreign keys to a Django model.
    """
    type_name = 'foreign key'

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

    def clean(self, name, data):
        value = super(ForeignKeyField, self).clean(name, data)
        queryset = self.queryset
        model = queryset.model
        try:
            return queryset.get(**{self.field: value})
        except model.DoesNotExist:
            raise ValidationException("Object does not exist")
        except model.MultipleObjectsReturned:
            return ValidationException("Multiple objects returned")

    def __copy__(self, **kwargs):
        return super(ForeignKeyField, self).__copy__(
            queryset=self.queryset, field=self.field,
            key_type=self.required_types)

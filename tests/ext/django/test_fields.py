from __future__ import absolute_import

from django.test import TestCase as DjangoTestCase

from valedictory.exceptions import (
    ValidationException, NoData)
from valedictory.ext.django import URLField, ForeignKeyField

from ...utils import ValidatorTestCase
from .models import TestModel


class TestURLField(ValidatorTestCase):

    field = URLField()

    def test_valid_urls(self):
        urls = [
            "http://example.com/",
            "https://example.com/test/?foo=bar",
            "https://user:pass@example.com/test/?foo=bar",
        ]
        for url in urls:
            self.assertEqual(url, self.field.clean(url))

    def test_required_url(self):
        with self.assertRaises(ValidationException):
            self.field.clean(NoData)

    def test_not_required_url(self):
        field = URLField(required=False)
        with self.assertRaises(NoData):
            field.clean(NoData)

    def test_invalid_url(self):
        with self.assertRaises(ValidationException):
            self.field.clean("nope")

    def test_invalid_type(self):
        with self.assertRaises(ValidationException):
            self.field.clean(True)


class TestForeignKeyField(ValidatorTestCase, DjangoTestCase):

    def test_valid_fk(self):
        field = ForeignKeyField(TestModel.objects.all())
        foo = TestModel.objects.create(name="foo")
        self.assertEqual(foo, field.clean(foo.pk))

    def test_invalid_fk(self):
        field = ForeignKeyField(TestModel.objects.all())
        with self.assertRaises(ValidationException) as cm:
            field.clean(1000)
        error = cm.exception
        self.assertEqual(error.msg, str(field.error_messages['missing']))

    def test_invalid_type(self):
        field = ForeignKeyField(TestModel.objects.all())
        foo = TestModel.objects.create(name="foo")
        with self.assertRaises(ValidationException):
            field.clean(str(foo.pk))

    def test_to_field(self):
        field = ForeignKeyField(TestModel.objects.all(), field="name",
                                key_type=str)
        foo = TestModel.objects.create(name="foo")
        bar = TestModel.objects.create(name="bar")

        self.assertEqual(foo, field.clean("foo"))
        self.assertEqual(bar, field.clean("bar"))

        with self.assertRaises(ValidationException):
            field.clean(foo.pk)

    def test_to_field_clash(self):
        field = ForeignKeyField(TestModel.objects.all(), field="name",
                                key_type=str)
        TestModel.objects.create(name="foo")
        TestModel.objects.create(name="foo")

        with self.assertRaises(ValidationException) as cm:
            field.clean("foo")
        error = cm.exception
        self.assertEqual(error.msg, field.error_messages['multiple'])

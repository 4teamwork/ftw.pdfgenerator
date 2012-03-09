# pylint: disable=W0212, W0201
# W0212: Access to a protected member of a client class
# W0201: Attribute defined outside __init__

from ftw.pdfgenerator.customization import LayoutCustomization
from ftw.pdfgenerator.interfaces import ICustomizableLayout
from ftw.pdfgenerator.interfaces import ILayoutCustomization
from ftw.pdfgenerator.templating import BaseTemplating
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from plone.mocktestcase import MockTestCase
from zope.component import adaptedBy
from zope.interface import Interface
from zope.interface.verify import verifyClass
import os.path



testdata_basedir = os.path.join(os.path.dirname(__file__),
                                'templates')
templates_foo = os.path.join(testdata_basedir, 'foo')
templates_bar = os.path.join(testdata_basedir, 'bar')
templates_baz = os.path.join(testdata_basedir, 'baz')


class TestLayoutCustomization(MockTestCase):

    adapter_class = LayoutCustomization

    layer = PDFGENERATOR_ZCML_LAYER

    def setUp(self):
        self.context = self.create_dummy()
        self.request = self.create_dummy()
        self.layout = self.create_dummy(
            get_template_directories=lambda: [])

    def test_implements_interface(self):
        self.assertTrue(ILayoutCustomization.implementedBy(
                self.adapter_class))
        verifyClass(ILayoutCustomization, self.adapter_class)

    def test_adapt_correctly(self):
        descriminators = adaptedBy(self.adapter_class)

        self.assertEqual(len(descriminators), 3)

        context_iface, request_iface, layout_iface = descriminators
        self.assertTrue(issubclass(context_iface, Interface))
        self.assertTrue(issubclass(request_iface, Interface))
        self.assertTrue(issubclass(layout_iface, ICustomizableLayout))

    def test_get_render_arguments(self):
        args = {}

        adapter = self.adapter_class(
            self.context, self.request, self.layout)

        self.assertTrue(isinstance(
                adapter.get_render_arguments(args), dict))

    def test_template(self):
        adapter = self.adapter_class(
            self.context, self.request, self.layout)

        if not adapter.template_name:
            return

        template = adapter.get_raw_template(adapter.template_name)

        self.assertIn('<%inherit file="original_layout"',
                      template)

    def test_get_template_directories_merges_layout_dirs(self):
        class Layout(BaseTemplating):
            template_directories = [templates_foo]

        class Customization(self.adapter_class):
            template_directories = [templates_bar]

        context = self.create_dummy()
        request = self.create_dummy()

        custom = Customization(context, request, Layout())
        directories = custom.get_template_directories()

        self.assertIn(templates_foo, directories)
        self.assertIn(templates_bar, directories)


class ExampleCustomization(LayoutCustomization):
    template_directories = [templates_baz]
    template_name = 'example_customization.tex'


class TestExampleCustomization(TestLayoutCustomization):
    adapter_class = ExampleCustomization

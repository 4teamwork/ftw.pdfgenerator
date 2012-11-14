# pylint: disable=W0212, W0201
# W0212: Access to a protected member of a client class
# W0201: Attribute defined outside __init__

from ftw.pdfgenerator.customization import LayoutCustomization
from ftw.pdfgenerator.interfaces import ICustomizableLayout
from ftw.pdfgenerator.interfaces import ILayoutCustomization
from ftw.pdfgenerator.templating import BaseTemplating
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from ftw.pdfgenerator.tests.example import ExampleCustomizableLayout
from ftw.pdfgenerator.tests.example import ExampleCustomization
from ftw.testing import MockTestCase
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

    def setUp(self, context=None, request=None, builder=None):
        super(TestLayoutCustomization, self).setUp()
        self.context = context or self.create_dummy()
        self.request = request or self.create_dummy()
        self.builder = builder or self.create_dummy()
        self.layout = ExampleCustomizableLayout(
            self.context, self.request, self.builder)

    def test_implements_interface(self):
        self.assertTrue(ILayoutCustomization.implementedBy(
                self.adapter_class))
        verifyClass(ILayoutCustomization, self.adapter_class)

    def test_adapts_correct(self):
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
        # pylint: disable=W0223
        # W0223: Method 'render_template' is abstract in
        # class 'BaseTemplating' but is not overridden
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


class TestExampleCustomization(TestLayoutCustomization):
    adapter_class = ExampleCustomization

    def test_add_template_file_from_customization_directory(self):
        layout = self.mocker.mock()
        self.expect(layout.get_template_directories()).result(
            [templates_foo])
        self.expect(layout.template_name).result('welcome.tex')

        self.expect(layout.builder.add_file('three.txt', data='bar three\n'))

        self.replay()

        adapter = ExampleCustomization(object(), object(), layout)
        adapter.add_raw_template_file('three.txt')

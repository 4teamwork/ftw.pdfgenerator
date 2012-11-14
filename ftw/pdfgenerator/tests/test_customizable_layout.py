from ftw.pdfgenerator.customization import LayoutCustomization
from ftw.pdfgenerator.interfaces import ICustomizableLayout
from ftw.pdfgenerator.interfaces import ILayoutCustomization
from ftw.pdfgenerator.layout.customizable import CustomizableLayout
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from ftw.pdfgenerator.tests.example import ExampleCustomizableLayout
from ftw.testing import MockTestCase
from zope.interface import Interface
from zope.interface.verify import verifyClass
import os.path


testdata_basedir = os.path.join(os.path.dirname(__file__),
                                'templates')
templates_bar = os.path.join(testdata_basedir, 'bar')
templates_baz = os.path.join(testdata_basedir, 'baz')


class TestCustomizableLayout(MockTestCase):

    layout_class = CustomizableLayout

    layer = PDFGENERATOR_ZCML_LAYER

    def setUp(self, context=None, request=None, builder=None):
        super(TestCustomizableLayout, self).setUp()
        self.context = context or self.create_dummy()
        self.request = request or self.create_dummy()
        self.builder = builder or self.create_dummy()

    def test_implements_interface(self):
        self.replay()
        self.assertTrue(ICustomizableLayout.implementedBy(self.layout_class))
        verifyClass(ICustomizableLayout, self.layout_class)

    def test_template_defines_slots(self):
        self.replay()
        layout = self.layout_class(self.context, self.request, self.builder)

        if not layout.template_name:
            return

        required_slots = [
            'documentclass',
            'usePackages',
            'beneathPackages',
            'aboveDocument',
            'documentTop',
            'documentBottom',
            ]

        template = layout.get_raw_template(layout.template_name)
        self.assertNotEqual(template, None)

        for slot in required_slots:
            self.assertIn('<%%block name="%s"' % slot, template)

    def test_logo_in_template(self):
        self.replay()
        layout = self.layout_class(self.context, self.request, self.builder)

        if not layout.template_name:
            return

        template = layout.get_raw_template(layout.template_name)
        self.assertNotEqual(template, None)
        self.assertIn('${logo}', template)

    def test_rendering_without_customization(self):
        self.replay()
        class Layout(self.layout_class):
            template_directories = [templates_baz]
            template_name = 'example_layout.tex'

        layout = Layout(self.context, self.request, self.builder)
        latex = layout.render_latex('CONTENT')

        self.assertIn(r'\begin{document}', latex)
        self.assertNotIn('my branding', latex)

    def test_rendering_with_customization_and_template(self):
        self.replay()
        class Layout(self.layout_class):
            template_directories = [templates_baz]
            template_name = 'example_layout.tex'

        class Customization(LayoutCustomization):
            template_directories = [templates_bar]
            template_name = 'example_customization.tex'

        self.mock_adapter(Customization, ILayoutCustomization,
                          (Interface, Interface, Interface))

        layout = Layout(self.context, self.request, self.builder)
        latex = layout.render_latex('CONTENT')

        self.assertIn(r'\begin{document}', latex)
        self.assertIn('my branding', latex)

    def test_rendering_with_customization_without_template(self):
        self.replay()
        class Layout(self.layout_class):
            template_directories = [templates_baz]
            template_name = 'example_layout.tex'

        class Customization(LayoutCustomization):
            template_directories = [templates_bar]
            template_name = None

            def before_render_hook(self):
                self.layout.use_package('otherpkg')

            def get_render_arguments(self, args):
                args['logo'] = 'THE-LOGO'
                return args

        self.mock_adapter(Customization, ILayoutCustomization,
                          (Interface, Interface, Interface))

        layout = Layout(self.context, self.request, self.builder)
        latex = layout.render_latex('CONTENT')

        self.assertIn(r'\begin{document}', latex)
        self.assertNotIn('my branding', latex)
        self.assertIn('THE-LOGO', latex)
        self.assertIn(r'\usepackage{otherpkg}', latex)


class TestExampleCustomizableLayout(TestCustomizableLayout):
    layout_class = ExampleCustomizableLayout

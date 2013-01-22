from ftw.pdfgenerator.interfaces import ITemplating, ILaTeXLayout
from ftw.pdfgenerator.layout.makolayout import MakoLayoutBase
from ftw.testing import MockTestCase
from zope.interface.verify import verifyClass
import os


class TestMakoLayoutBase(MockTestCase):

    def setUp(self):
        super(TestMakoLayoutBase, self).setUp()
        testdata_basedir = os.path.join(
            os.path.dirname(__file__), 'templates')

        self.templates_foo = os.path.join(testdata_basedir, 'foo')

    def test_implements_interfaces(self):
        self.assertTrue(ITemplating.implementedBy(MakoLayoutBase))
        verifyClass(ITemplating, MakoLayoutBase)

        self.assertTrue(ILaTeXLayout.implementedBy(MakoLayoutBase))
        verifyClass(ILaTeXLayout, MakoLayoutBase)

    def test_render_with_arguments(self):
        class FooLayout(MakoLayoutBase):
            template_directories = [self.templates_foo]
            template_name = 'titlepage.tex'

            def get_render_arguments(self):
                return {'title': 'hello world!!!'}

        foo = FooLayout(object(), object(), object())
        self.assertEqual(
            foo.render_latex(''),
            '\\title{hello world!!!}\n\n\\maketitle\n\n')

    def test_default_render_arguments(self):
        layout = MakoLayoutBase(object(), object(), object())
        self.assertEqual(layout.get_render_arguments(), {})

    def test_fails_if_no_default_template(self):
        class BarLayout(MakoLayoutBase):
            pass

        bar = BarLayout(object(), object(), object())

        with self.assertRaises(ValueError) as cm:
            bar.render_latex('')

        self.assertEqual(
        str(cm.exception),
        'BarLayout: `template_name` is not defined.')

    def test_add_raw_template_file(self):
        class FooLayout(MakoLayoutBase):
            template_directories = [self.templates_foo]

        builder = self.mocker.mock()
        self.expect(builder.add_file(
                'welcome.tex', data='{\\large Hello \\textbf{${view.name}}!}\n'))

        self.replay()

        foo = FooLayout(object(), object(), builder)
        foo.add_raw_template_file('welcome.tex')

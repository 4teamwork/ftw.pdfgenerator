# pylint: disable=R0801
# R0801: Similar lines in 3 files

from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.view import MakoLaTeXView
from plone.mocktestcase import MockTestCase
from zope.interface.verify import verifyClass
import os


class TestMakoLaTeXView(MockTestCase):

    def setUp(self):
        super(TestMakoLaTeXView, self).setUp()
        testdata_basedir = os.path.join(os.path.dirname(__file__),
                                        'templates')

        self.templates_foo = os.path.join(testdata_basedir, 'foo')

    def test_implements_interface(self):
        self.assertTrue(ILaTeXView.implementedBy(MakoLaTeXView))
        verifyClass(ILaTeXView, MakoLaTeXView)

    def test_adapted_objects_are_stored_right(self):
        context = object()
        request = object()
        layout = object()

        obj = MakoLaTeXView(context, request, layout)
        self.assertEquals(obj.context, context)
        self.assertEquals(obj.request, request)
        self.assertEquals(obj.layout, layout)

    def test_register_template_file_plain(self):
        context = object()
        request = object()
        layout = self.mocker.mock()
        self.expect(layout.get_builder().add_file('one.txt', 'foo one\n'))

        class FooView(MakoLaTeXView):
            template_directories = [self.templates_foo]

        self.replay()
        FooView(context, request, layout).register_template_file('one.txt')

    def test_register_template_file_rendererd(self):
        context = object()
        request = object()
        layout = self.mocker.mock()
        self.expect(layout.get_builder().add_file(
                'titlepage.tex',
                '\\title{Hello World}\n\n\\maketitle\n\n'))

        class FooView(MakoLaTeXView):
            template_directories = [self.templates_foo]

        self.replay()
        FooView(context, request, layout).register_template_file(
            'titlepage.tex', render=True, title='Hello World')

    def test_default_rendering_fails_if_template_name_not_defined(self):
        context = request = layout = object()

        class FooView(MakoLaTeXView):
            pass

        with self.assertRaises(ValueError) as cm:
            FooView(context, request, layout).render()

        self.assertEqual(str(cm.exception),
                         'FooView: `template_name` is not defined.')

    def test_default_rendering_with_arguments(self):
        context = request = layout = object()

        class FooView(MakoLaTeXView):
            template_directories = [self.templates_foo]
            template_name = 'titlepage.tex'

            def get_render_arguments(self):
                return {'title': 'My diary'}

        self.assertEqual(FooView(context, request, layout).render(),
                         '\\title{My diary}\n\n\\maketitle\n\n')

    def test_default_rendering_with_view_access(self):
        context = request = layout = object()

        class FooView(MakoLaTeXView):
            template_directories = [self.templates_foo]
            template_name = 'welcome.tex'

            @property
            def name(self):
                return 'Hugo Boss'

        self.assertEqual(FooView(context, request, layout).render(),
                         '{\\large Hello {\\bf Hugo Boss}!}\n')

# pylint: disable=R0801
# R0801: Similar lines in 3 files

from ftw.pdfgenerator.interfaces import ILaTeXView, IRecursiveLaTeXView
from ftw.pdfgenerator.layout.baselayout import BaseLayout
from ftw.pdfgenerator.view import MakoLaTeXView, RecursiveLaTeXView
from ftw.testing import MockTestCase
from mock import patch
from zope.interface import Interface
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
        layout = self.mock()

        class FooView(MakoLaTeXView):
            template_directories = [self.templates_foo]

        FooView(context, request, layout).register_template_file('one.txt')
        layout.get_builder.return_value.add_file.assert_called_with(
            'one.txt', 'foo one\n')

    def test_register_template_file_rendererd(self):
        context = object()
        request = object()
        layout = self.mock()

        class FooView(MakoLaTeXView):
            template_directories = [self.templates_foo]

        FooView(context, request, layout).register_template_file(
            'titlepage.tex', render=True, title='Hello World')
        layout.get_builder.return_value.add_file.assert_called_with(
            'titlepage.tex', '\\title{Hello World}\n\n\\maketitle\n\n')

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
                         '{\\large Hello \\textbf{Hugo Boss}!}\n')

    def test_convert_passes_to_converter(self):
        context = request = object()
        layout = self.mock()
        converter = self.mock()

        html = 'this <b>is</b> html\n '
        latex = 'this \textbf{is} html'

        layout.get_converter.return_value = converter
        converter.convert.return_value = latex

        view = MakoLaTeXView(context, request, layout)
        self.assertEqual(view.convert(html, trim=True), latex)

    def test_convert_plain_passes_to_converter(self):
        context = request = object()
        layout = self.mock()
        converter = self.mock()

        html = 'this is <not> html\n '
        latex = 'this is <not> html'

        layout.get_converter.return_value = converter
        converter.convert_plain.return_value = latex

        view = MakoLaTeXView(context, request, layout)
        self.assertEqual(view.convert_plain(html, trim=True), latex)


class TestRecursiveLaTeXView(MockTestCase):

    def test_implements_interface(self):
        self.assertTrue(IRecursiveLaTeXView.implementedBy(RecursiveLaTeXView))
        verifyClass(IRecursiveLaTeXView, RecursiveLaTeXView)

    def test_adapted_objects_are_stored_right(self):
        context = object()
        request = object()
        layout = object()

        obj = RecursiveLaTeXView(context, request, layout)
        self.assertEquals(obj.context, context)
        self.assertEquals(obj.request, request)
        self.assertEquals(obj.layout, layout)

    def test_render_children(self):
        request = {}
        builder = object()

        context = self.mock()
        obj1 = self.mock()
        obj2 = self.mock()

        layout = BaseLayout(context, request, builder)

        context.listFolderContents.return_value = [obj1, obj2]

        class Subview(object):
            def __init__(self, context, request, layout):
                self.context = context

            def render(self):
                if self.context == obj1:
                    return 'object one latex'
                elif self.context == obj2:
                    return 'object two latex'

        self.mock_adapter(Subview, ILaTeXView,
                          (Interface, Interface, Interface))

        view = RecursiveLaTeXView(context, request, layout)
        self.assertEqual(view.render_children(),
                         'object one latex\nobject two latex')

    def test_render_children__folder_contents_selected_objects(self):
        request = {'paths': [
                '/plone/parent/child1',
                '/plone/parent/child3']}
        builder = object()

        context = self.mock()
        child1 = self.mock()
        child2 = self.mock()
        child3 = self.mock()

        base_path = ['', 'plone', 'parent']
        child1.getPhysicalPath.return_value = base_path + ['child1']
        child2.getPhysicalPath.return_value = base_path + ['child2']
        child3.getPhysicalPath.return_value = base_path + ['child3']

        context.listFolderContents.return_value = [child1, child2, child3]

        layout = BaseLayout(context, request, builder)

        class Subview(object):
            def __init__(self, context, request, layout):
                self.context = context

            def render(self):
                if self.context == child1:
                    return 'child one latex'
                elif self.context == child3:
                    return 'child three latex'

        self.mock_adapter(Subview, ILaTeXView,
                          (Interface, Interface, Interface))

        view = RecursiveLaTeXView(context, request, layout)
        self.assertEqual(
            view.render_children(),
            'child one latex\nchild three latex')

    def test_get_render_arguments_contains_latex_content(self):
        context = request = layout = object()
        view = RecursiveLaTeXView(context, request, layout)

        with patch(
            'ftw.pdfgenerator.tests.test_view.RecursiveLaTeXView.render_children'
        ) as mocked_render_childern:
            mocked_render_childern.return_value = 'children latex'

            self.assertEqual(view.get_render_arguments(),
                             {'latex_content': 'children latex'})

    def test_paths_respected_when_not_on_context(self):
        request = {'paths': [
                '/plone/parent/child1']}
        builder = object()

        context = self.mock()
        child1 = self.mock()
        child1a = self.mock()

        base_path = ['', 'plone', 'parent']
        child1.getPhysicalPath.return_value = base_path + ['child1']
        child1a.getPhysicalPath.return_value = base_path + ['child1', 'child1a']

        child1.listFolderContents.return_value = [child1a]

        layout = BaseLayout(context, request, builder)

        subview = self.mock()
        self.mock_adapter(subview, ILaTeXView,
                          (Interface, Interface, Interface))

        subview.return_value.render.return_value = 'child one A latex'

        view = RecursiveLaTeXView(child1, request, layout)
        self.assertEqual(
            view.render_children(),
            'child one A latex')

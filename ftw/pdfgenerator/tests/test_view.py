# pylint: disable=R0801
# R0801: Similar lines in 3 files

from ftw.pdfgenerator.interfaces import ILaTeXView, IRecursiveLaTeXView
from ftw.pdfgenerator.layout.baselayout import BaseLayout
from ftw.pdfgenerator.view import MakoLaTeXView, RecursiveLaTeXView
from ftw.testing import MockTestCase
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
                         '{\\large Hello \\textbf{Hugo Boss}!}\n')

    def test_convert_passes_to_converter(self):
        context = request = object()
        layout = self.mocker.mock()
        converter = self.mocker.mock()

        html = 'this <b>is</b> html\n '
        latex = 'this \textbf{is} html'

        self.expect(layout.get_converter()).result(converter)
        self.expect(converter.convert(html, trim=True)).result(latex)

        self.replay()

        view = MakoLaTeXView(context, request, layout)
        self.assertEqual(view.convert(html, trim=True), latex)

    def test_convert_plain_passes_to_converter(self):
        context = request = object()
        layout = self.mocker.mock()
        converter = self.mocker.mock()

        html = 'this is <not> html\n '
        latex = 'this is <not> html'

        self.expect(layout.get_converter()).result(converter)
        self.expect(converter.convert_plain(html, trim=True)).result(latex)

        self.replay()

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

        context = self.mocker.mock()
        obj1 = self.mocker.mock()
        obj2 = self.mocker.mock()

        layout = BaseLayout(context, request, builder)

        self.expect(context.listFolderContents()).result([obj1, obj2])

        subview = self.mocker.mock()
        self.mock_adapter(subview, ILaTeXView,
                          (Interface, Interface, Interface))

        self.expect(subview(obj1, request, layout).render()).result(
            'object one latex')
        self.expect(subview(obj2, request, layout).render()).result(
            'object two latex')

        self.replay()

        view = RecursiveLaTeXView(context, request, layout)
        self.assertEqual(view.render_children(),
                         'object one latex\nobject two latex')

    def test_render_children__folder_contents_selected_objects(self):
        request = {'paths': [
                '/plone/parent/child1',
                '/plone/parent/child3']}
        builder = object()

        context = self.mocker.mock(count=False)
        child1 = self.mocker.mock(count=False)
        child2 = self.mocker.mock(count=False)
        child3 = self.mocker.mock(count=False)

        base_path = ['', 'plone', 'parent']
        self.expect(child1.getPhysicalPath()).result(base_path + ['child1'])
        self.expect(child2.getPhysicalPath()).result(base_path + ['child2'])
        self.expect(child3.getPhysicalPath()).result(base_path + ['child3'])

        self.expect(context.listFolderContents()).result(
            [child1, child2, child3])

        layout = BaseLayout(context, request, builder)

        subview = self.mocker.mock()
        self.mock_adapter(subview, ILaTeXView,
                          (Interface, Interface, Interface))

        self.expect(subview(child1, request, layout).render()).result(
            'child one latex')
        self.expect(subview(child3, request, layout).render()).result(
            'child three latex')

        self.replay()

        view = RecursiveLaTeXView(context, request, layout)
        self.assertEqual(
            view.render_children(),
            'child one latex\nchild three latex')

    def test_get_render_arguments_contains_latex_content(self):
        context = request = layout = object()
        view = self.mocker.patch(RecursiveLaTeXView(
                context, request, layout))

        self.expect(view.render_children()).result('children latex')

        self.replay()

        self.assertEqual(view.get_render_arguments(),
                         {'latex_content': 'children latex'})

    def test_paths_respected_when_not_on_context(self):
        request = {'paths': [
                '/plone/parent/child1']}
        builder = object()

        context = self.mocker.mock(count=False)
        child1 = self.mocker.mock(count=False)
        child1a = self.mocker.mock(count=False)

        base_path = ['', 'plone', 'parent']
        self.expect(child1.getPhysicalPath()).result(base_path + ['child1'])
        self.expect(child1a.getPhysicalPath()).result(base_path + [
                'child1', 'child1a'])

        self.expect(child1.listFolderContents()).result([child1a])

        layout = BaseLayout(context, request, builder)

        subview = self.mocker.mock()
        self.mock_adapter(subview, ILaTeXView,
                          (Interface, Interface, Interface))

        self.expect(subview(child1a, request, layout).render()).result(
            'child one A latex')

        self.replay()

        view = RecursiveLaTeXView(child1, request, layout)
        self.assertEqual(
            view.render_children(),
            'child one A latex')

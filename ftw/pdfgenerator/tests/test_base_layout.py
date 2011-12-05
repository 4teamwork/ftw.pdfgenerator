# pylint: disable=W0212, W0201
# W0212: Access to a protected member of a client class
# W0201: Attribute defined outside __init__

from ftw.pdfgenerator.exceptions import ConflictingUsePackageOrder
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import ILaTeXView
from ftw.pdfgenerator.layout.baselayout import BaseLayout
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from plone.mocktestcase import MockTestCase
from zope.component import adaptedBy, provideAdapter
from zope.interface import Interface, implements
from zope.interface import alsoProvides, directlyProvides
from zope.interface.verify import verifyClass


class TestBaseLayout(MockTestCase):

    layer = PDFGENERATOR_ZCML_LAYER

    def setUp(self):
        self.builder = self.create_dummy()
        directlyProvides(self.builder, IBuilder)


    def test_implements_interface(self):
        self.assertTrue(ILaTeXLayout.implementedBy(BaseLayout))
        verifyClass(ILaTeXLayout, BaseLayout)

    def test_adapts(self):
        # BaseLayout should adapt three things (context, request, builder).
        self.assertEquals(len(adaptedBy(BaseLayout)), 3)

    def test_use_package(self):
        layout = BaseLayout(self.create_dummy(), self.create_dummy(),
                            self.builder)

        self.assertEqual(layout.get_packages_latex(), '')

        layout.use_package('inputenc', 'utf8')
        self.assertEqual(layout.get_packages_latex(),
                         '\\usepackage[utf8]{inputenc}\n')

        layout.use_package(u'titlesec', 'noindentafter',
                           insert_after='inputenc')
        self.assertEqual(layout.get_packages_latex(),
                         '\\usepackage[utf8]{inputenc}\n'
                         '\\usepackage[noindentafter]{titlesec}\n')

        layout.use_package('titlesec', 'largestsep')
        self.assertEqual(
            layout.get_packages_latex(),
            '\\usepackage[utf8]{inputenc}\n'
            '\\usepackage[noindentafter, largestsep]{titlesec}\n')

        layout.use_package('titlesec', 'largestsep')
        self.assertEqual(
            layout.get_packages_latex(),
            '\\usepackage[utf8]{inputenc}\n'
            '\\usepackage[noindentafter, largestsep]{titlesec}\n')

        layout.use_package('titlesec', options='', append_options=False)
        self.assertEqual(
            layout.get_packages_latex(),
            '\\usepackage[utf8]{inputenc}\n'
            '\\usepackage{titlesec}\n')

    def test_use_package_bad_package_name(self):
        layout = BaseLayout(self.create_dummy(), self.create_dummy(),
                            self.builder)

        with self.assertRaises(ValueError) as cm:
            layout.use_package(None)

        self.assertEqual(
            str(cm.exception),
            'Package name should be a string, got None (NoneType)')

        with self.assertRaises(ValueError) as cm:
            layout.use_package(5)

        self.assertEqual(
            str(cm.exception),
            'Package name should be a string, got 5 (int)')

    def test_remove_package(self):
        layout = BaseLayout(self.create_dummy(), self.create_dummy(),
                            self.builder)
        self.assertEqual(layout.get_packages_latex(), '')

        layout.use_package('color')
        layout.use_package('colortbl')
        layout.use_package('dcolumn')

        self.assertEqual(
            layout.get_packages_latex(),
            '\\usepackage{color}\n'
            '\\usepackage{colortbl}\n'
            '\\usepackage{dcolumn}\n')

        layout.remove_package('color')
        self.assertEqual(
            layout.get_packages_latex(),
            '\\usepackage{colortbl}\n'
            '\\usepackage{dcolumn}\n')

        layout.remove_package('*')
        self.assertEqual(layout.get_packages_latex(), '')

    def test_use_package_order(self):
        # use_package in combination with insert_after
        # should also work when the "other" package is not yet registered.

        layout = BaseLayout(self.create_dummy(), self.create_dummy(),
                            self.builder)
        self.assertEqual(layout.get_packages_latex(), '')

        # test insert_after
        layout.use_package('dcolumn', insert_after='color')
        layout.use_package('color')
        layout.use_package('colortbl')

        self.assertEqual(
            layout.get_packages_latex(),
            '\\usepackage{color}\n'
            '\\usepackage{dcolumn}\n'
            '\\usepackage{colortbl}\n')

        layout.remove_package('*')
        self.assertEqual(layout.get_packages_latex(), '')

    def test_use_package_conflicting_order(self):
        # Using use_package with conflicting orders should raise exceptions

        layout = BaseLayout(self.create_dummy(), self.create_dummy(),
                            self.builder)
        self.assertEqual(layout.get_packages_latex(), '')

        # insert_after itself
        with self.assertRaises(ConflictingUsePackageOrder) as cm:
            layout.use_package('foo', insert_after='foo')

        self.assertEqual(
            str(cm.exception),
            'Cannot insert "foo" after itself (insert_after="foo").')

        self.assertEqual(layout.get_packages_latex(), '')

        # recursive conflicting order
        layout.use_package('baz', insert_after='foo')
        layout.use_package('foo', insert_after='bar')
        with self.assertRaises(ConflictingUsePackageOrder) as cm:
            layout.use_package('bar', insert_after='baz')

        self.assertEqual(
            str(cm.exception),
            'Conflicting order: bar after baz after foo after bar.')

    def test_render_latex_raises_not_implemented(self):
        # The BaseLayout does not specify how to render the LaTeX.
        layout = BaseLayout(self.create_dummy(), self.create_dummy(),
                            self.builder)

        with self.assertRaises(NotImplementedError):
            layout.render_latex('latex')

    def test_get_builder_returns_builder(self):
        context = self.create_dummy()
        request = self.create_dummy()
        builder = self.create_dummy()
        layout = BaseLayout(context, request, builder)

        self.assertEqual(layout.get_builder(), builder)

    def test_get_converter_keeps_instance(self):
        context = self.create_dummy()
        request = self.create_dummy()
        builder = self.create_dummy()

        layout = BaseLayout(context, request, builder)

        self.assertNotEqual(layout.get_converter(), None)
        self.assertEqual(layout.get_converter(), layout.get_converter())

    def test_get_view_rendering(self):
        class IFoo(Interface): pass

        foo = self.create_dummy()
        alsoProvides(foo, IFoo)

        class FooView(object):
            implements(ILaTeXView)
            data = 'foo'

            def __init__(self, context, request, layout):
                pass

            def render(self):
                return self.data
        provideAdapter(FooView, (IFoo, Interface, Interface), name='')

        class PreFooView(FooView):
            data = 'pre'
        provideAdapter(PreFooView, (IFoo, Interface, Interface),
                       name='pre-hook')

        class PostFooView(FooView):
            data = 'post'
        provideAdapter(PostFooView, (IFoo, Interface, Interface),
                       name='post-hook')

        context = self.create_dummy()
        request = self.create_dummy()
        builder = self.create_dummy()
        layout = BaseLayout(context, request, builder)

        views = layout.get_views_for(foo)
        self.assertEqual(len(views), 3)
        self.assertEqual(type(views[0]), PreFooView)
        self.assertEqual(type(views[1]), FooView)
        self.assertEqual(type(views[2]), PostFooView)

        self.assertEqual(
            layout.render_latex_for(foo), 'pre\nfoo\npost')

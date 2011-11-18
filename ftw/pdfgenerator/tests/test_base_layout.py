# pylint: disable=W0212, W0201
# W0212: Access to a protected member of a client class
# W0201: Attribute defined outside __init__

from ftw.pdfgenerator.exceptions import ConflictingUsePackageOrder
from ftw.pdfgenerator.interfaces import IBuilderFactory
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.layout.baselayout import BaseLayout
from plone.mocktestcase import MockTestCase
from zope.component import adaptedBy
from zope.interface.verify import verifyClass


class TestBaseLayout(MockTestCase):

    def test_implements_interface(self):
        self.assertTrue(ILaTeXLayout.implementedBy(BaseLayout))
        verifyClass(ILaTeXLayout, BaseLayout)

    def test_adapts_context_and_request(self):
        # BaseLayout should adapt two things (context and request).
        self.assertEquals(len(adaptedBy(BaseLayout)), 2)

    def test_use_package(self):
        layout = BaseLayout(self.create_dummy(), self.create_dummy())

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
        layout = BaseLayout(self.create_dummy(), self.create_dummy())

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
        layout = BaseLayout(self.create_dummy(), self.create_dummy())
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

        layout = BaseLayout(self.create_dummy(), self.create_dummy())
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

        layout = BaseLayout(self.create_dummy(), self.create_dummy())
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

    def test_get_builder_is_lazy(self):
        builderfactory = self.mocker.mock()
        self.mock_utility(builderfactory, IBuilderFactory)

        layout_state = 'nothing done'
        self.expect(builderfactory()).call(lambda: layout_state)
        self.replay()

        layout = BaseLayout(self.create_dummy(), self.create_dummy())
        layout_state = 'initialized'

        self.assertEqual(layout.get_builder(), 'initialized')

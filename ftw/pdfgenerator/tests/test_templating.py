# pylint: disable=W0223, C0102
# W0223: Method 'XX' is abstract in class 'YY' but is not overridden
# C0102: Black listed name "foo"



from ftw.pdfgenerator.interfaces import ITemplating
from ftw.pdfgenerator.templating import BaseTemplating
from ftw.pdfgenerator.templating import MakoTemplating
from unittest2 import TestCase
from zope.interface.verify import verifyClass
import os


class TestBaseTemplating(TestCase):

    def setUp(self):
        super(TestBaseTemplating, self).setUp()
        testdata_basedir = os.path.join(os.path.dirname(__file__),
                                        'templates')

        self.templates_foo = os.path.join(testdata_basedir, 'foo')
        self.templates_bar = os.path.join(testdata_basedir, 'bar')
        self.templates_baz = os.path.join(testdata_basedir, 'baz')

        self.templates_not_existing = os.path.join(testdata_basedir,
                                                   'not-existing')
        assert not os.path.exists(self.templates_not_existing)

    def test_implements_interface(self):
        self.assertTrue(ITemplating.implementedBy(BaseTemplating))
        verifyClass(ITemplating, BaseTemplating)

    def test_template_directories_order(self):
        class Foo(BaseTemplating):
            template_directories = [self.templates_foo,
                                    self.templates_bar]

        self.assertEqual(Foo().get_template_directories(),
                         [self.templates_bar, self.templates_foo])

    def test_template_directories_are_inherited(self):
        class Foo(BaseTemplating):
            template_directories = [self.templates_foo]

        class Bar(Foo):
            template_directories = [self.templates_bar]

        self.assertEqual(Bar().get_template_directories(),
                         [self.templates_bar,
                          self.templates_foo])

    def test_relative_directories_are_converted(self):
        class Foo(BaseTemplating):
            # his is the relative path to self.templates_foo, since it is
            # in the folder "tests".
            template_directories = ['templates/foo']

        self.assertEqual(Foo().get_template_directories(),
                         [self.templates_foo])

    def test_template_directories_is_None_does_not_fail(self):
        class Foo(BaseTemplating):
            template_directories = [self.templates_foo]

        class Bar(Foo):
            template_directories = None

        class Baz(Bar):
            template_directories = [self.templates_baz]

        self.assertEqual(Baz().get_template_directories(),
                         [self.templates_baz,
                          self.templates_foo])

    def test_template_directories_not_defined_does_not_duplicate(self):
        class Foo(BaseTemplating):
            template_directories = [self.templates_foo]

        class Bar(Foo):
            pass

        self.assertEqual(Bar().get_template_directories(),
                         [self.templates_foo])

    def test_template_directories_fails_if_definition_of_wrong_type(self):
        class Foo(BaseTemplating):
            template_directories = 1

        with self.assertRaises(ValueError) as cm:
            Foo().get_template_directories()

        self.assertEqual(
            str(cm.exception),
            'Foo.template_directories should be a list or None.')

        class Bar(BaseTemplating):
            template_directories = 1

        class Baz(Bar):
            pass

        with self.assertRaises(ValueError) as cm:
            Baz().get_template_directories()

        self.assertEqual(
            str(cm.exception),
            'Baz.template_directories should be a list or None.')

    def test_template_directories_fails_if_path_not_existing(self):
        class Foo(BaseTemplating):
            template_directories = [self.templates_not_existing]

        with self.assertRaises(OSError) as cm:
            Foo().get_template_directories()

        # OSError seems to be strange defined, so that the context manager
        # converts it to a list..
        self.assertEqual(cm.exception[1], 'No such file or directory')

    def test_get_template_returns_template(self):
        class Foo(BaseTemplating):
            template_directories = [self.templates_foo]
            # has: one.txt, two.txt, three.txt

        class Bar(Foo):
            template_directories = [self.templates_bar]
            # has: two.txt, three.txt

        class Baz(Bar):
            template_directories = [self.templates_baz]
            # has: three.txt

        obj = Baz()
        self.assertEqual(obj.get_template('one.txt'), 'foo one\n')
        self.assertEqual(obj.get_template('two.txt'), 'bar two\n')
        self.assertEqual(obj.get_template('three.txt'), 'baz three\n')

        class BarBaz(BaseTemplating):
            template_directories = [self.templates_baz,
                                    self.templates_bar]

        class FooBarBaz(BarBaz):
            template_directories = [self.templates_foo]

        obj = FooBarBaz()
        self.assertEqual(obj.get_template('one.txt'), 'foo one\n')
        self.assertEqual(obj.get_template('two.txt'), 'foo two\n')
        self.assertEqual(obj.get_template('three.txt'), 'foo three\n')

    def test_get_tempalte_returns_None_if_template_not_found(self):
        class Foo(BaseTemplating):
            template_directories = [self.templates_foo]

        self.assertEqual(Foo().get_template('not-existing.txt'), None)
        self.assertEqual(
            BaseTemplating().get_template('not-existing.txt'), None)

    def test_render_template_raises_not_implemented(self):
        # BaseTemplating does not specific a template engine - therefore
        # it is not able to render any templates. It should raise a
        # NotImplementedError.

        class Foo(BaseTemplating):
            template_directories = [self.templates_foo]

        with self.assertRaises(NotImplementedError) as cm:
            Foo().render_template('foo.txt')

        self.assertEqual(
            str(cm.exception),
            'render_template() is not implemented on BaseTemplating.')


class TestMakoTemplating(TestCase):

    def setUp(self):
        super(TestMakoTemplating, self).setUp()
        testdata_basedir = os.path.join(os.path.dirname(__file__),
                                        'templates')

        self.templates_foo = os.path.join(testdata_basedir, 'foo')
        self.templates_bar = os.path.join(testdata_basedir, 'bar')
        self.templates_baz = os.path.join(testdata_basedir, 'baz')

    def test_render_template_renders_template(self):
        class Foo(MakoTemplating):
            template_directories = [self.templates_foo]

        obj = Foo()
        self.assertEqual(
            obj.render_template('titlepage.tex', title='Wohoo'),
            '\\title{Wohoo}\n\n\\maketitle\n\n')

    def test_render_template_with_inheritance(self):
        class Foo(MakoTemplating):
            template_directories = [self.templates_foo]

        class Bar(Foo):
            template_directories = [self.templates_bar]

        obj = Bar()
        self.assertEqual(
            obj.render_template('customtitlepage.tex', title='foo',
                                custom='bar'),
            '\\title{foo}\n\n{\\large\\textbf{bar}}\n\n')

    def test_render_template_view_access(self):
        class Foo(MakoTemplating):
            template_directories = [self.templates_foo]

            def __init__(self):
                MakoTemplating.__init__(self)
                self.name = 'John'

        foo = Foo()
        self.assertEqual(
            foo.render_template('welcome.tex'),
            '{\\large Hello \\textbf{John}!}\n')

    def test_get_raw_template(self):
        class Foo(MakoTemplating):
            template_directories = [self.templates_foo]

        foo = Foo()
        self.assertEqual(
            foo.get_raw_template('welcome.tex'),
            r'{\large Hello \textbf{${view.name}}!}' + '\n')

    def test_get_raw_template_returns_None_if_template_not_found(self):
        class Foo(MakoTemplating):
            template_directories = [self.templates_foo]

        foo = Foo()
        self.assertEqual(
            foo.get_raw_template('this-file-does-not-exist'),
            None)

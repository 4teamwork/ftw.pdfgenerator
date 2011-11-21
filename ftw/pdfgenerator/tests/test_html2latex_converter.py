from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.html2latex import converter
from ftw.pdfgenerator.html2latex import subconverter
from plone.mocktestcase import MockTestCase
from unittest2 import TestCase
from zope.interface.verify import verifyClass


MODE_REPLACE = interfaces.HTML2LATEX_MODE_REPLACE
MODE_REGEXP = interfaces.HTML2LATEX_MODE_REGEXP
MODE_REGEXP_FUNCTION = interfaces.HTML2LATEX_MODE_REGEXP_FUNCTION
DEFAULT_PLACEHOLDER = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER


class TestCustomPatternPlaceholderWrapper(TestCase):

    def test_placeholder_wrapper(self):
        placeholder = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM
        mode = interfaces.HTML2LATEX_MODE_REGEXP_FUNCTION

        wrapper = converter.CustomPatternAtPlaceholderWrapper(
            mode=mode,
            placeholder=placeholder)

        self.assertEqual(wrapper.mode, mode)
        self.assertEqual(wrapper.placeholder, placeholder)


class TestBasePatternAware(TestCase):

    def setUp(self):
        super(TestBasePatternAware, self).setUp()

        self.pattern1 = (MODE_REPLACE, '{', '\\{')
        self.pattern2 = (MODE_REPLACE, '}', '\\}')
        self.pattern3 = (MODE_REPLACE, '&nbsp;', ' ')
        self.pattern4 = (MODE_REPLACE, '\r\n', ' ')
        self.pattern5 = (MODE_REPLACE, '\r', ' ')
        self.pattern6 = (MODE_REPLACE, '\n', ' ')

    def test_register_patterns_at_default_placeholder(self):
        obj = converter.BasePatternAware(
            [self.pattern1,
             self.pattern2,
             DEFAULT_PLACEHOLDER,
             self.pattern3])

        obj.register_patterns([self.pattern4, self.pattern5])

        self.assertEqual(
            obj.patterns,
            [self.pattern1,
             self.pattern2,
             self.pattern4,
             self.pattern5,
             DEFAULT_PLACEHOLDER,
             self.pattern3,])

    def test_register_patterns_with_placeholder_wrapper(self):
        top = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_TOP
        obj = converter.BasePatternAware(
            [top,
             self.pattern1,
             DEFAULT_PLACEHOLDER,
             self.pattern2])

        special_pattern = (
            converter.CustomPatternAtPlaceholderWrapper(
                mode=MODE_REGEXP,
                placeholder=top),
            r'\w{5, 7}', ' ')
        special_pattern_unwrapped = [MODE_REGEXP, r'\w{5, 7}', ' ']

        obj.register_patterns([special_pattern])

        self.assertEqual(
            obj.patterns,
            [special_pattern_unwrapped,
             top,
             self.pattern1,
             DEFAULT_PLACEHOLDER,
             self.pattern2])

    def test_register_patterns_overwrite_existing(self):
        obj = converter.BasePatternAware(
            [self.pattern1,
             DEFAULT_PLACEHOLDER])

        custom = list(self.pattern1)
        custom[2] = 'foo'
        custom = tuple(custom)

        obj.register_patterns([custom])

        self.assertEqual(
            obj.patterns,
            [custom,
             DEFAULT_PLACEHOLDER])

    def test_register_subconverters(self):
        obj = converter.BasePatternAware([DEFAULT_PLACEHOLDER])

        class Foo(subconverter.SubConverter):
            pattern = 'foo'
            placeholder = DEFAULT_PLACEHOLDER

        obj.register_subconverters([Foo])

        self.assertEqual(
            obj.patterns,
            [(MODE_REGEXP_FUNCTION, 'foo', Foo),
             DEFAULT_PLACEHOLDER])


class TestHTML2LatexConverter(MockTestCase):

    def test_implements_interface(self):
        self.assertTrue(interfaces.IHTML2LaTeXConverter.implementedBy(
                converter.HTML2LatexConverter))
        verifyClass(interfaces.IHTML2LaTeXConverter,
                    converter.HTML2LatexConverter)

    def test_converter_uses_copy_of_default_subconverters(self):
        class NoSubconvertersConverter(converter.HTML2LatexConverter):
            def get_default_subconverters(self):
                return []

        obj = NoSubconvertersConverter(
            object(), object(), object(), object())

        self.assertEqual(obj.patterns, converter.DEFAULT_PATTERNS)
        self.assertNotEqual(id(obj.patterns), id(converter.DEFAULT_PATTERNS))

    def test_convert_with_custom_pattern(self):
        obj = converter.HTML2LatexConverter(
            object(), object(), object(), object())

        self.assertEqual(
            obj.convert('foo bar baz', custom_patterns=[
                    (MODE_REPLACE, 'bar', 'replaced')]),
            'foo replaced baz')

    def test_convert_with_custom_subconverter(self):
        class MyConverter(subconverter.SubConverter):
            pattern = 'bar'

            def __call__(self):
                self.replace(r'{\bf replaced}')

        obj = converter.HTML2LatexConverter(
            object(), object(), object(), object())

        self.assertEqual(
            obj.convert('foo bar baz bar', custom_subconverters=[
                    MyConverter]),
            r'foo {\bf replaced} baz {\bf replaced}')


class TestHTML2LaTeXConvertRunner(MockTestCase):

    def test_implements_interface(self):
        self.assertTrue(interfaces.IHTML2LaTeXConvertRunner.implementedBy(
                converter.HTML2LatexConvertRunner))
        verifyClass(interfaces.IHTML2LaTeXConvertRunner,
                    converter.HTML2LatexConvertRunner)


    def test_raises_when_initializied_with_non_converter(self):
        with self.assertRaises(ValueError) as cm:
            converter.HTML2LatexConvertRunner(object(), [], '')

        self.assertEqual(str(cm.exception),
                         'converter should by a IHTML2LaTeXConverter')

    def test_raises_when_convert_started_twice(self):
        obj = converter.HTML2LatexConverter(
            object(), object(), object(), object())
        runner = converter.HTML2LatexConvertRunner(obj, [], '')

        runner.runner_convert()
        with self.assertRaises(RuntimeError) as cm:
            runner.runner_convert()

        self.assertEqual(str(cm.exception),
                         'runner_convert() should not be called twice!')

# pylint: disable=W0212, W0201
# W0212: Access to a protected member of a client class
# W0201: Attribute defined outside __init__

from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.html2latex import converter
from ftw.pdfgenerator.html2latex import subconverter
from ftw.pdfgenerator.html2latex import wrapper
from ftw.pdfgenerator.layout.baselayout import BaseLayout
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from ftw.testing import MockTestCase
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass


MODE_REPLACE = interfaces.HTML2LATEX_MODE_REPLACE
MODE_REGEXP = interfaces.HTML2LATEX_MODE_REGEXP
MODE_REGEXP_FUNCTION = interfaces.HTML2LATEX_MODE_REGEXP_FUNCTION
DEFAULT_PLACEHOLDER = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER


class TestCustomPatternPlaceholderWrapper(TestCase):

    def test_placeholder_wrapper(self):
        placeholder = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM
        mode = interfaces.HTML2LATEX_MODE_REGEXP_FUNCTION

        wrap = wrapper.CustomPatternAtPlaceholderWrapper(
            mode=mode,
            placeholder=placeholder)

        self.assertEqual(wrap.mode, mode)
        self.assertEqual(wrap.placeholder, placeholder)


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
            wrapper.CustomPatternAtPlaceholderWrapper(
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

    def test_reigster_custom_pattern_with_noreplace(self):
        obj = converter.BasePatternAware([
                self.pattern1,
                DEFAULT_PLACEHOLDER])

        custom = list(self.pattern1)
        custom[2] = 'foo'
        custom = tuple(custom)

        obj._insert_custom_pattern(custom, replace=False)

        self.assertEqual(
            obj.patterns,
            [self.pattern1,
             custom,
             DEFAULT_PLACEHOLDER])

    def test_register_wrapper_replacing(self):
        top = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_TOP
        obj = converter.BasePatternAware(
            [top,
             self.pattern1,
             DEFAULT_PLACEHOLDER])

        custom = [
            wrapper.CustomPatternAtPlaceholderWrapper(
                mode=self.pattern1[0],
                placeholder=top),
            self.pattern1[1],
            'foo']

        obj.register_patterns([custom])

        self.assertEqual(
            obj.patterns,
            [[self.pattern1[0], self.pattern1[1], 'foo'],
             top,
             self.pattern1,
             DEFAULT_PLACEHOLDER])

    def test_register_subconverters(self):
        obj = converter.BasePatternAware([DEFAULT_PLACEHOLDER])

        class Foo(subconverter.SubConverter):
            pattern = 'foo'
            placeholder = DEFAULT_PLACEHOLDER

            def __call__(self):
                return ''

        obj.register_subconverters([Foo])

        self.assertEqual(
            obj.patterns,
            [(MODE_REGEXP_FUNCTION, 'foo', Foo),
             DEFAULT_PLACEHOLDER])

    def test_get_subconverter_by_pattern(self):
        obj = converter.BasePatternAware([DEFAULT_PLACEHOLDER])

        class Foo(subconverter.SubConverter):
            pattern = 'foo'
            placeholder = DEFAULT_PLACEHOLDER

            def __call__(self):
                return ''

        class Bar(Foo):
            pattern = 'bar'

        class Baz(Foo):
            pattern = 'baz'

        obj.register_subconverters([Foo, Bar, Baz])
        self.assertEqual(obj.get_subconverter_by_pattern('foo'), Foo)
        self.assertEqual(obj.get_subconverter_by_pattern('bar'), Bar)
        self.assertEqual(obj.get_subconverter_by_pattern('baz'), Baz)
        self.assertEqual(obj.get_subconverter_by_pattern('unkown'), None)


class TestHTML2LatexConverter(MockTestCase):

    layer = PDFGENERATOR_ZCML_LAYER

    def test_implements_interface(self):
        self.assertTrue(interfaces.IHTML2LaTeXConverter.implementedBy(
                converter.HTML2LatexConverter))
        verifyClass(interfaces.IHTML2LaTeXConverter,
                    converter.HTML2LatexConverter)

    def test_default_converter_adapter_registration(self):
        context = self.create_dummy()
        request = self.create_dummy()
        builder = self.create_dummy()
        layout = BaseLayout(context, request, builder)

        obj = getMultiAdapter((context, request, layout),
                              interfaces.IHTML2LaTeXConverter)

        self.assertEqual(obj.__class__, converter.HTML2LatexConverter)

    def test_converter_uses_copy_of_default_subconverters(self):
        class NoSubconvertersConverter(converter.HTML2LatexConverter):
            def get_default_subconverters(self):
                return []

        obj = NoSubconvertersConverter(
            object(), object(), object())

        self.assertEqual(obj.patterns, converter.DEFAULT_PATTERNS)
        self.assertNotEqual(id(obj.patterns), id(converter.DEFAULT_PATTERNS))

    def test_convert_with_custom_pattern(self):
        obj = converter.HTML2LatexConverter(
            object(), object(), object())

        self.assertEqual(
            obj.convert('foo bar baz', custom_patterns=[
                    (MODE_REPLACE, 'bar', 'replaced')]),
            'foo replaced baz')

    def test_convert_with_custom_subconverter(self):
        class MyConverter(subconverter.SubConverter):
            pattern = 'bar'

            def __call__(self):
                self.replace(r'\textbf{replaced}')

        obj = converter.HTML2LatexConverter(
            object(), object(), object())

        self.assertEqual(
            obj.convert('foo bar baz bar', custom_subconverters=[
                    MyConverter]),
            r'foo \textbf{replaced} baz \textbf{replaced}')

    def test_convert_plain(self):
        obj = converter.HTML2LatexConverter(
            object(), object(), object())

        self.assertEqual(obj.convert('foo <bar> baz'), 'foo  baz')
        self.assertEqual(obj.convert_plain('foo <bar> baz'), 'foo <bar> baz')

    def test_quoted_umlaut(self):
        obj = converter.HTML2LatexConverter(
            object(), object(), object())

        self.assertEqual(
            '"Uber h"ofliche B"urger aus Rh\xc3\xb4ne-Alpes',
            obj.quoted_umlauts(
                '\xc3\x9cber h\xc3\xb6fliche B\xc3\xbcrger'
                ' aus Rh\xc3\xb4ne-Alpes'))


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
            object(), object(), object())
        runner = converter.HTML2LatexConvertRunner(obj, [], '')

        runner.runner_convert()
        with self.assertRaises(RuntimeError) as cm:
            runner.runner_convert()

        self.assertEqual(str(cm.exception),
                         'runner_convert() should not be called twice!')

    def test_quoted_umlaut(self):
        obj = converter.HTML2LatexConverter(
            object(), object(), object())
        runner = converter.HTML2LatexConvertRunner(obj, [], '')

        self.assertEqual(
            '"Uber h"ofliche B"urger aus Rh\xc3\xb4ne-Alpes',
            runner.quoted_umlauts(
                '\xc3\x9cber h\xc3\xb6fliche B\xc3\xbcrger'
                ' aus Rh\xc3\xb4ne-Alpes'))

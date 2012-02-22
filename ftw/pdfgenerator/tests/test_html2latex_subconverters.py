from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.pdfgenerator.html2latex.subconverter import SubConverter
from ftw.pdfgenerator.html2latex.subconverters import htmlentities
from ftw.pdfgenerator.html2latex.subconverters import listing
from ftw.pdfgenerator.interfaces import ISubConverter
from plone.mocktestcase import MockTestCase
from unittest2 import TestCase
from zope.interface.verify import verifyClass
import re


class SubconverterTestBase(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.converter = HTML2LatexConverter(
            context=object(),
            request=object(),
            layout=object())

        self.convert = self.converter.convert


class TestBaseSubConverter(MockTestCase):

    def test_implements_interface(self):
        self.assertTrue(ISubConverter.implementedBy(SubConverter))
        verifyClass(ISubConverter, SubConverter)

    def test_init(self):
        converter = object()
        match = object()
        html = object()

        obj = SubConverter(converter=converter, match=match, html=html)
        self.assertEqual(obj.converter, converter)
        self.assertEqual(obj.match, match)
        self.assertEqual(obj.fullhtml, html)

    def test_call_not_implemented(self):
        converter = match = html = object()
        obj = SubConverter(converter, match, html)

        with self.assertRaises(NotImplementedError):
            obj()

    def test_get_html_returns_matched_html(self):
        html = 'one three five'
        match = re.search('t[\w]*', html)

        obj = SubConverter(object(), match, html)
        self.assertEqual(obj.get_html(), 'three')

    def test_replace_and_lock_passed_to_converter(self):
        html = 'one three five'
        match = re.search('t[\w]*', html)
        converter = self.mocker.mock()

        self.expect(converter.replace_and_lock(4, 9, 'latex code'))

        self.replay()

        obj = SubConverter(converter, match, html)
        obj.replace_and_lock('latex code')

    def test_replace_passed_to_converter(self):
        html = 'one three five'
        match = re.search('t[\w]*', html)
        converter = self.mocker.mock()

        self.expect(converter.replace(4, 9, 'latex code'))

        self.replay()

        obj = SubConverter(converter, match, html)
        obj.replace('latex code')

    def test_get_context(self):
        context = self.mocker.mock()
        self.expect(context.found())

        class MySubConverter(SubConverter):
            pattern = 'y'

            def __call__(self):
                self.get_context().found()

        self.replay()

        converter = HTML2LatexConverter(
            context=context,
            request=object(),
            layout=object())

        converter.convert('xyz', custom_subconverters=[MySubConverter])

    def test_get_layout(self):
        layout = self.mocker.mock()
        self.expect(layout.found())

        class MySubConverter(SubConverter):
            pattern = 'y'

            def __call__(self):
                self.get_layout().found()

        self.replay()

        converter = HTML2LatexConverter(
            context=object(),
            request=object(),
            layout=layout)

        converter.convert('xyz', custom_subconverters=[MySubConverter])


class TestHtmlentitiesConverter(SubconverterTestBase):

    def test_converter_is_default(self):
        self.assertIn(
            htmlentities.HtmlentitiesConverter,
            self.converter.get_default_subconverters())

    def test_converter_converts_umlauts(self):
        self.assertEqual(self.convert('&auml;&euml;&iuml;&ouml;&uuml;'),
                         '\xc3\xa4\xc3\xab\xc3\xaf\xc3\xb6\xc3\xbc')
        self.assertEqual(self.convert('5 &lt; 6'),
                         '5 < 6')
        self.assertEqual(self.convert('Hello&nbsp;World'),
                         'Hello World')

    def test_converter_converts_xmlentities(self):
        # "&" should also be escaped by a later pattern.
        self.assertEqual(self.convert('m&#38;m'),
                         r'm\&m')


class TestListConverter(SubconverterTestBase):

    def test_converter_is_default(self):
        self.assertIn(
            listing.ListConverter,
            self.converter.get_default_subconverters())

    def test_converts_lists_with_win_paths(self):
        self.assertEqual(
            self.convert('<ul><li>O:\\foo\\bar\\baz</li></ul>'),
            '\\begin{itemize}\n'
            '\\item O:\\\\foo\\\\bar\\\\baz\n'
            '\\end{itemize}\n')

        self.assertEqual(
            self.convert('<ul><li>One</li><li>Two</li><li>Three</li></ul>'),
            '\\begin{itemize}\n\\item One\n\\item Two\n\\item Three\n'
            '\\end{itemize}\n')

        self.assertEqual(
            self.convert('<ol>\n<li>First</li>\n<li>Second</li>\n'
                         '<li>Third</li>\n</ol>'),
            '\\begin{enumerate}\n\\item First\n\\item Second\n'
            '\\item Third\n\\end{enumerate}\n')

    def test_ordered_lists(self):
        html = '\n'.join((
                '<ol>',
                '    <li>a</li>',
                '    <li>b',
                '        <ol><li>ba</li></ol>',
                '    </li>',
                '    <li>c</li>',
                '</ol>'))

        latex = '\n'.join((
                '\\begin{enumerate}',
                '\\item a',
                '\\item b         \\begin{enumerate}',
                '\\item ba',
                '\\end{enumerate}',
                '\\item c',
                '\\end{enumerate}',
                ''))

        self.assertEqual(self.convert(html), latex)

    def test_unorderd_lists(self):
        html = '\n'.join(('<ul>',
                          '    <li>a</li>',
                          '    <li>b',
                          '        <ul>',
                          '            <li>ba</li>',
                          '            <li>bb</li>',
                          '        </ul>',
                          '    </li>',
                          '    <li>c</li>',
                          '</ul>'))

        latex = '\n'.join((r'\begin{itemize}',
                           r'\item a',
                           r'\item b         \begin{itemize}',
                           r'\item ba',
                           r'\item bb',
                           r'\end{itemize}',
                           r'\item c',
                           r'\end{itemize}',
                           r''))

        self.assertEqual(self.convert(html), latex)

    def test_list_values_are_converted(self):
        html = '<ul><li>This is <b>important</b>!</ul>'
        latex = '\n'.join((r'\begin{itemize}',
                           r'\item This is {\bf important}!',
                           r'\end{itemize}',
                           r''))

        self.assertEqual(self.convert(html), latex)

    def test_list_with_attributes_matches(self):
        html = '<ul style="list-style-type: square;" class="simple">' + \
            '<li>Any text</li></ul>'
        latex = '\n'.join((r'\begin{itemize}',
                           r'\item Any text',
                           r'\end{itemize}',
                           r''))

        self.assertEqual(self.convert(html), latex)

    def test_multiple_lists_at_once(self):
        html = '\n'.join((
                '<ul><li>foo</li><li>bar</li></ul>',
                '<b>foobar</b>',
                '<ul><li>foo</li><li>bar</li></ul>'))

        latex = '\n'.join((
                r'\begin{itemize}',
                r'\item foo',
                r'\item bar',
                r'\end{itemize}',
                r'',
                r'{\bf foobar}',
                r'',
                r'\begin{itemize}',
                r'\item foo',
                r'\item bar',
                r'\end{itemize}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_wrong_match(self):
        html = '<ulwrong><li>foo</li></ulwrong>'

        latex = 'foo'

        self.assertEqual(self.convert(html), latex)

    def test_bad_html_fallback(self):
        html = '\n'.join((
                '<ul>',
                '<li>foo</li>',
                'bar',
                '</ul>'))

        latex = '\n'.join((
                r'\begin{itemize}',
                r'\item foo',
                r'bar',
                r'\end{itemize}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_definition_list(self):
        html = '\n'.join((
                '<dl>',
                '<dt>definition term</dt>',
                '<dd>THE definition</dd>',
                '<dt>another term</dt>',
                '<dd>another definition</dd>',
                '</dl>'))

        latex = '\n'.join((
                r'\begin{description}',
                r'\item[definition term] THE definition',
                r'\item[another term] another definition',
                r'\end{description}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_nested_definition_list(self):
        html = '\n'.join((
                '<dl>',
                '<dt>definition term</dt>',
                '<dd>THE definition</dd>',
                '<dt>nested</dt>',
                '<dd><dl><dt>subterm</dt><dd>subdef</dd></dl></dd>',
                '<dt>another term</dt>',
                '<dd>another definition</dd>',
                '</dl>'))

        latex = '\n'.join((
                r'\begin{description}',
                r'\item[definition term] THE definition',
                r'\item[nested] \begin{description}',
                r'\item[subterm] subdef',
                r'\end{description}',
                r'\item[another term] another definition',
                r'\end{description}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_no_list_with_no_elements(self):
        html = '\n'.join((
                'foo',
                '<ul></ul>',
                'bar',
                '<dl>',
                '</dl>',
                'baz',
                '<ol> </ol>'))

        latex = 'foo  bar  baz '

        self.assertEqual(self.convert(html), latex)

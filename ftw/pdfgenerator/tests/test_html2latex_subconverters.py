from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.pdfgenerator.html2latex.subconverter import SubConverter
from ftw.pdfgenerator.html2latex.subconverters import htmlentities
from ftw.pdfgenerator.html2latex.subconverters import listing
from ftw.pdfgenerator.html2latex.subconverters import table
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
            layout=object(),
            builder=object())

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


class TestTableConverter(MockTestCase):

    def convert(self, *args, **kwargs):
        count = 1
        if 'count' in kwargs:
            count = kwargs['count']
            del kwargs['count']

        layout = self.mocker.mock()
        self.expect(layout.use_package('longtable')).count(count)
        self.expect(layout.use_package('multirow')).count(count)
        self.expect(layout.use_package('multicol')).count(count)

        self.replay()

        converter = HTML2LatexConverter(
            context=object(),
            request=object(),
            layout=layout,
            builder=object())

        return converter.convert(*args, **kwargs)

    def test_converter_is_default(self):
        converter = HTML2LatexConverter(
            context=object(),
            request=object(),
            layout=object(),
            builder=object())

        self.assertIn(
            table.TableConverter,
            converter.get_default_subconverters())

    def test_table_converted_to_longtable(self):
        html = '\n'.join((
                r'<table>',
                r'    <thead>',
                r'        <tr><th>My Head</th></tr>',
                r'    </thead><tbody>',
                r'        <tr><td>My Body</td></tr>',
                r'    </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{l}',
                r'\multicolumn{1}{l}{My Head} \\',
                r'\endhead',
                r'\multicolumn{1}{l}{My Body} \\',
                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_headings(self):
        html = '\n'.join((
                r'<table>',
                r'    <thead>',
                r'        <tr>',
                r'            <td>headA</td>',
                r'            <td>headB</td>',
                r'        </tr>',
                r'    </thead>',
                r'    <tbody>',
                r'        <tr>',
                r'            <td>1A</td>',
                r'            <td>1B</td>',
                r'        </tr>',
                r'        <tr>',
                r'            <td>2A</td>',
                r'            <td>2B</td>',
                r'        </tr>',
                r'    </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{ll}',
                r'\multicolumn{1}{l}{headA} & \multicolumn{1}{l}{headB} \\',
                r'\endhead',
                r'\multicolumn{1}{l}{1A} & \multicolumn{1}{l}{1B} \\',
                r'\multicolumn{1}{l}{2A} & \multicolumn{1}{l}{2B} \\',
                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_colgroup_with_width(self):
        html = '\n'.join((
                r'<table>',
                r'    <colgroup>',
                r'        <col width="30%" />',
                r'        <col width="70%" />',
                r'    </colgroup>',
                r'    <tbody>',
                r'        <tr>',
                r'            <td>test1</td>',
                r'            <td>test2</td>',
                r'        </tr><tr>',
                r'            <td>test3</td>',
                r'            <td>test4</td>',
                r'        </tr>',
                r'    </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{p{0.3\linewidth}p{0.7\linewidth}}',

                r'\multicolumn{1}{p{0.3\linewidth}}{test1} & '
                r'\multicolumn{1}{p{0.7\linewidth}}{test2} \\',

                r'\multicolumn{1}{p{0.3\linewidth}}{test3} & '
                r'\multicolumn{1}{p{0.7\linewidth}}{test4} \\',

                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_col_and_cell_have_widths(self):
        # Colgroup sizes should work even if the alignment is defined
        # on the cell

        html = '\n'.join((
                r'<table>',
                r'    <colgroup>',
                r'        <col width="30%" />',
                r'        <col width="70%" />',
                r'    </colgroup>',
                r'    <tbody>',
                r'        <tr>',
                r'            <td align="right">test1</td>',
                r'            <td align="left">test2</td>',
                r'        </tr><tr>',
                r'            <td align="center">test3</td>',
                r'            <td>test4</td>',
                r'        </tr>',
                r'    </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{p{0.3\linewidth}p{0.7\linewidth}}',

                r'\multicolumn{1}{p{0.3\linewidth}}{'
                r'\raggedleft test1} & \multicolumn{1}{'
                r'p{0.7\linewidth}}{\raggedright test2} \\',

                r'\multicolumn{1}{p{0.3\linewidth}}{\center\vspace{-1.5em}'
                r'test3} & \multicolumn{1}{p{0.7\linewidth}}{test4} \\',

                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_caption_is_used(self):
        # The table caption is used and will be shown in the table index

        html = '\n'.join((
                r'<table>',
                r'    <caption>Testtabelle</caption>',
                r'    <tr><td>test</td></tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{l}',
                r'\caption{Testtabelle} \\',
                r'\multicolumn{1}{l}{test} \\',
                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_caption_not_listed(self):
        # It is also possible to add a caption whithout showing the table
        # in the table index by adding the css class "notListed"

        html = '\n'.join((
                r'<table class="notListed">',
                r'    <caption>NotIndexedCaption</caption>',
                r'    <tr><td>foo</td></tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{l}',
                r'\caption*{NotIndexedCaption} \\',
                r'\multicolumn{1}{l}{foo} \\',
                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_caption_at_bottom(self):
        # For putting the caption to the bottom of table, just at the
        # <caption>-Tag at the bottom:

        html = '\n'.join((
                r'<table>',
                r'    <tr><td>foo</td></tr>',
                r'    <caption>My Table</caption>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{l}',
                r'\multicolumn{1}{l}{foo} \\',
                r'\caption{My Table} \\',
                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)


    def test_multiple_tables(self):
        # Multiple tables should work as well

        html = r'<table><tr><td>test1</td></tr></table>' + \
            r'<table><tr><td>test2</td></tr></table>'

        latex = '\n'.join((
                r'\begin{longtable}{l}',
                r'\multicolumn{1}{l}{test1} \\',
                r'\end{longtable}',
                r'\begin{longtable}{l}',
                r'\multicolumn{1}{l}{test2} \\',
                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html, count=2), latex)

    def test_convert_cell_html(self):
        # Table cells can contain other HTML which will be converted as well

        html = r'<table><tr><td><b>Hello</b> <i>World</i></td></tr></table>'

        latex = '\n'.join((
                r'\begin{longtable}{l}',
                r'\multicolumn{1}{l}{{\bf Hello} {\it World}} \\',
                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_convert_other_html(self):
        # HTML around the Table should be converted as well

        html = '\n'.join((
                r'This <i>is</i> a <b>Table</b>:<br />',
                r'<table><tr><td>test</td></tr></table>',
                r'<b>yeah</b>'))

        latex = '\n'.join((
                r'This {\it is} a {\bf Table}:\\',
                r' \begin{longtable}{l}',
                r'\multicolumn{1}{l}{test} \\',
                r'\end{longtable}',
                r' {\bf yeah}'))

        self.assertEqual(self.convert(html), latex)


    def test_htmlentities(self):
        # We should be able to use html entities (minidom has some
        # problems with htmlentites..)

        html = '\n'.join((
                r'<table>',
                r' <tr><td>2&gt;1</td></tr>',
                r' <tr><td>X&auml;Y</td></tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{l}',
                r'\multicolumn{1}{l}{2>1} \\',
                '\\multicolumn{1}{l}{X\xc3\xa4Y} \\\\',
                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_colspan(self):
        # The td-Attribute "colspan" should work as well

        html = '\n'.join((
                r'<table>',
                r'    <colgroup>',
                r'        <col width="33%" />',
                r'        <col width="33%" />',
                r'        <col width="34%" />',
                r'    </colgroup>',
                r'    <tr>',
                r'        <td>one</td>',
                r'        <td>two</td>',
                r'        <td>three</td>',
                r'    </tr><tr>',
                r'        <td colspan="2">one and two</td>',
                r'        <td>three</td>',
                r'    </tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{p{0.33\linewidth}p{0.33\linewidth}'
                r'p{0.34\linewidth}}',

                r'\multicolumn{1}{p{0.33\linewidth}}{one} & '
                r'\multicolumn{1}{p{0.33\linewidth}}{two} & '
                r'\multicolumn{1}{p{0.34\linewidth}}{three} \\',

                r'\multicolumn{2}{p{0.66\linewidth}}{one and two} & '
                r'\multicolumn{1}{p{0.34\linewidth}}{three} \\',

                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_rowspan(self):
        # The td-Attribute "rowspan" should work as well

        html = '\n'.join((
                r'<table>',
                r'    <colgroup>',
                r'        <col width="50%"/>',
                r'        <col width="50%"/>',
                r'    </colgroup>',
                r'    <tr>',
                r'        <td rowspan="2">one</td>',
                r'        <td>two</td>',
                r'    </tr><tr>',
                r'        <td>three</td>',
                r'    </tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{p{0.5\linewidth}p{0.5\linewidth}}',

                r'\multirow{2}{0.5\textwidth}{one} & \multicolumn{1}'
                r'{p{0.5\linewidth}}{two} \\',

                r' & \multicolumn{1}{p{0.5\linewidth}}{three} \\',
                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_gridborder(self):

        html = '\n'.join((
                r'<table border="1">',
                r'    <colgroup>',
                r'        <col width="30%" />',
                r'        <col width="70%" />',
                r'    </colgroup>',
                r'    <tbody>',
                r'        <tr>',
                r'            <td>test1</td>',
                r'            <td>test2</td>',
                r'        </tr><tr>',
                r'            <td>test3</td>',
                r'            <td>test4</td>',
                r'        </tr>',
                r'    </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{longtable}{|p{0.3\linewidth}|p{0.7\linewidth}|}',
                r'\hline',

                r'\multicolumn{1}{|p{0.3\linewidth}|}{test1} & '
                r'\multicolumn{1}{p{0.7\linewidth}|}{test2} \\',

                r'\hline',

                r'\multicolumn{1}{|p{0.3\linewidth}|}{test3} & '
                r'\multicolumn{1}{p{0.7\linewidth}|}{test4} \\',

                r'\hline',
                r'\end{longtable}',
                r''))

        self.assertEqual(self.convert(html), latex)

from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.pdfgenerator.html2latex.subconverters import table
from plone.mocktestcase import MockTestCase


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
            layout=layout)

        return converter.convert(*args, **kwargs)

    def test_converter_is_default(self):
        converter = HTML2LatexConverter(
            context=object(),
            request=object(),
            layout=object())

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

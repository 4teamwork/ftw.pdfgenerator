from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.pdfgenerator.html2latex.subconverters import table
from plone.mocktestcase import MockTestCase
from unittest2 import TestCase


class TestTableConverter(MockTestCase):

    def convert(self, *args, **kwargs):
        count = 1
        if 'count' in kwargs:
            count = kwargs['count']
            del kwargs['count']

        if 'longtable' in kwargs:
            longtable = kwargs['longtable']
            del kwargs['longtable']
        else:
            longtable = False

        layout = self.mocker.mock()
        if longtable:
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

    def test_table_converted(self):
        html = '\n'.join((
                r'<table>',
                r'    <thead>',
                r'        <tr><th>My Head</th></tr>',
                r'    </thead><tbody>',
                r'        <tr><td>My Body</td></tr>',
                r'    </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{My Head} \\',
                r'\multicolumn{1}{l}{My Body} \\',
                r'\end{tabular}',
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
                r'\begin{tabular}{ll}',
                r'\multicolumn{1}{l}{headA} & \multicolumn{1}{l}{headB} \\',
                r'\multicolumn{1}{l}{1A} & \multicolumn{1}{l}{1B} \\',
                r'\multicolumn{1}{l}{2A} & \multicolumn{1}{l}{2B} \\',
                r'\end{tabular}',
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
                r'\begin{tabular}{p{0.3\linewidth}p{0.7\linewidth}}',

                r'\multicolumn{1}{p{0.3\linewidth}}{test1} & '
                r'\multicolumn{1}{p{0.7\linewidth}}{test2} \\',

                r'\multicolumn{1}{p{0.3\linewidth}}{test3} & '
                r'\multicolumn{1}{p{0.7\linewidth}}{test4} \\',

                r'\end{tabular}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_colgroup_with_invalid_width(self):
        html = '\n'.join((
                r'<table>',
                r'    <colgroup>',
                r'        <col width="30%" />',
                r'        <col width="bad value" align="right" />',
                r'    </colgroup>',
                r'    <tbody>',
                r'        <tr>',
                r'            <td>test1</td>',
                r'            <td>test2</td>',
                r'        </tr>',
                r'    </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{tabular}{p{0.3\linewidth}r}',

                r'\multicolumn{1}{p{0.3\linewidth}}{test1} & '
                r'\multicolumn{1}{r}{test2} \\',

                r'\end{tabular}',
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
                r'\begin{tabular}{p{0.3\linewidth}p{0.7\linewidth}}',

                r'\multicolumn{1}{p{0.3\linewidth}}{'
                r'\raggedleft test1} & \multicolumn{1}{'
                r'p{0.7\linewidth}}{\raggedright test2} \\',

                r'\multicolumn{1}{p{0.3\linewidth}}{\center\vspace{-1.5em}'
                r'test3} & \multicolumn{1}{p{0.7\linewidth}}{test4} \\',

                r'\end{tabular}',
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
                r'\begin{tabular}{l}',
                r'\caption{Testtabelle} \\',
                r'\multicolumn{1}{l}{test} \\',
                r'\end{tabular}',
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
                r'\begin{tabular}{l}',
                r'\caption*{NotIndexedCaption} \\',
                r'\multicolumn{1}{l}{foo} \\',
                r'\end{tabular}',
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
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{foo} \\',
                r'\caption{My Table} \\',
                r'\end{tabular}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_multiple_tables(self):
        # Multiple tables should work as well

        html = r'<table><tr><td>test1</td></tr></table>' + \
            r'<table><tr><td>test2</td></tr></table>'

        latex = '\n'.join((
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{test1} \\',
                r'\end{tabular}',
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{test2} \\',
                r'\end{tabular}',
                r''))

        self.assertEqual(self.convert(html, count=2), latex)

    def test_convert_cell_html(self):
        # Table cells can contain other HTML which will be converted as well

        html = r'<table><tr><td><b>Hello</b> <i>World</i></td></tr></table>'

        latex = '\n'.join((
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{{\bf Hello} {\it World}} \\',
                r'\end{tabular}',
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
                r' \begin{tabular}{l}',
                r'\multicolumn{1}{l}{test} \\',
                r'\end{tabular}',
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
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{2>1} \\',
                '\\multicolumn{1}{l}{X\xc3\xa4Y} \\\\',
                r'\end{tabular}',
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
                r'\begin{tabular}{p{0.33\linewidth}p{0.33\linewidth}'
                r'p{0.34\linewidth}}',

                r'\multicolumn{1}{p{0.33\linewidth}}{one} & '
                r'\multicolumn{1}{p{0.33\linewidth}}{two} & '
                r'\multicolumn{1}{p{0.34\linewidth}}{three} \\',

                r'\multicolumn{2}{p{0.66\linewidth}}{one and two} & '
                r'\multicolumn{1}{p{0.34\linewidth}}{three} \\',

                r'\end{tabular}',
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
                r'\begin{tabular}{p{0.5\linewidth}p{0.5\linewidth}}',

                r'\multirow{2}{0.5\textwidth}{one} & \multicolumn{1}'
                r'{p{0.5\linewidth}}{two} \\',

                r' & \multicolumn{1}{p{0.5\linewidth}}{three} \\',
                r'\end{tabular}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_complex_rowspan_colspan(self):
        html = '\n'.join((
                r'<table>',
                r'  <colgroup>',
                r'    <col width="25%" />',
                r'    <col width="25%" />',
                r'    <col width="25%" />',
                r'    <col width="25%" />',
                r'  </colgroup>',
                r'  <tr>',
                r'    <td>A1</td>',
                r'    <td rowspan="2">B1-B2</td>',
                r'    <td>C1</td>',
                r'    <td>D1</td>',
                r'  </tr>',
                r'  <tr>',
                r'    <td>A2</td>',
                r'    <td rowspan="2">C2-C3</td>',
                r'    <td>D2</td>',
                r'  </tr>',
                r'  <tr>',
                r'    <td colspan="2">A3-B3</td>',
                r'    <td colspan="2">D3-E3</td>',
                r'  </tr>',
                r'</table>',
                ))

        latex = '\n'.join((
                r'\begin{tabular}{p{0.25\linewidth}p{0.25\linewidth}' + \
                    r'p{0.25\linewidth}p{0.25\linewidth}l}',

                # row 1
                r'\multicolumn{1}{p{0.25\linewidth}}{A1} & ' + \
                    r'\multirow{2}{0.25\textwidth}{B1-B2} & ' + \
                    r'\multicolumn{1}{p{0.25\linewidth}}{C1} & ' + \
                    r'\multicolumn{1}{p{0.25\linewidth}}{D1} \\',

                # row 2
                r'\multicolumn{1}{p{0.25\linewidth}}{A2} & ' + \
                    r' & '
                    r'\multirow{2}{0.25\textwidth}{C2-C3} & ' + \
                    r'\multicolumn{1}{p{0.25\linewidth}}{D2} \\',

                # row 3
                r'\multicolumn{2}{p{0.5\linewidth}}{A3-B3} & ' + \
                    r' & '
                    r'\multicolumn{2}{l}{D3-E3} \\',

                r'\end{tabular}',
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
                r'\begin{tabular}{|p{0.3\linewidth}|p{0.7\linewidth}|}',
                r'\hline',

                r'\multicolumn{1}{|p{0.3\linewidth}}{test1} & '
                r'\multicolumn{1}{|p{0.7\linewidth}|}{test2} \\',

                r'\hline',

                r'\multicolumn{1}{|p{0.3\linewidth}}{test3} & '
                r'\multicolumn{1}{|p{0.7\linewidth}|}{test4} \\',

                r'\hline',
                r'\end{tabular}',
                r''))

        self.assertEqual(self.convert(html), latex)

    def test_newlines(self):
        # In LaTeX, there should not be a "\\" or "\n" in a table cell, but
        # a "\newline". The newline only is taken in account if the cell or
        # column is defined with a fixed width ("p{width}").

        html = '\n'.join((
                r'<table>',
                r'  <tr>',
                r'    <td width="50%">hello<br />world</td>',
                r'    <td width="50%"><p>foo</p><p>bar</p></td>',
                r'  </tr>',
                r'</table>',
                ))

        latex = '\n'.join((
                r'\begin{tabular}{p{0.5\linewidth}p{0.5\linewidth}}',

                r'\multicolumn{1}{p{0.5\linewidth}}{' + \
                    r'hello\newline world} & ' + \
                    r'\multicolumn{1}{p{0.5\linewidth}}{' + \
                    r'foo\newline \newline bar} \\',

                r'\end{tabular}',
                r''
                ))

        self.assertEqual(self.convert(html), latex)

    def test_tabular_environment_depends_on_table_size(self):
        # For big tables we use the "tabular" environment, allowing a table
        # to be splitted up over multiple pages, but for short tables we use
        # the longtable environment.

        tabular_html = '\n'.join((
                r'<table>',
                r'  <tr>',
                r'    <td width="50%">foo</td>',
                r'    <td width="50%">bar</td>',
                r'  </tr>',
                r'</table>',
                ))

        tabular_latex = '\n'.join((
                r'\begin{tabular}{p{0.5\linewidth}p{0.5\linewidth}}',

                r'\multicolumn{1}{p{0.5\linewidth}}{' + \
                    r'foo} & ' + \
                    r'\multicolumn{1}{p{0.5\linewidth}}{' + \
                    r'bar} \\',

                r'\end{tabular}',
                r''
                ))

        self.assertEqual(self.convert(tabular_html), tabular_latex)

    def test_longtable_environment_depends_on_table_size(self):
        # For big tables we use the "tabular" environment, allowing a table
        # to be splitted up over multiple pages, but for short tables we use
        # the longtable environment.

        longtable_html = '\n'.join((
                r'<table>',
                40 * r'<tr><td>foo</td></tr>',
                r'</table>',
                ))

        longtable_latex = '\n'.join((
                r'\begin{longtable}{l}',
                (40 * '\\multicolumn{1}{l}{foo} \\\\\n').strip(),
                r'\end{longtable}',
                r''
                ))

        self.assertEqual(self.convert(longtable_html, longtable=True),
                         longtable_latex)

    def test_longtable_environment_enforcable_by_cssclass(self):
        longtable_html = '\n'.join((
                r'<table class="page-break">',
                r'  <tr>',
                r'    <td width="50%">foo</td>',
                r'    <td width="50%">bar</td>',
                r'  </tr>',
                r'</table>',
                ))

        longtable_latex = '\n'.join((
                r'\begin{longtable}{p{0.5\linewidth}p{0.5\linewidth}}',

                r'\multicolumn{1}{p{0.5\linewidth}}{' + \
                    r'foo} & ' + \
                    r'\multicolumn{1}{p{0.5\linewidth}}{' + \
                    r'bar} \\',

                r'\end{longtable}',
                r''
                ))

        self.assertEqual(self.convert(longtable_html, longtable=True),
                         longtable_latex)

    def test_tabular_environment_enforcable_by_cssclass(self):
        tabular_html = '\n'.join((
                r'<table class="no-page-break">',
                20 * r'<tr><td>foo</td></tr>',
                r'</table>',
                ))

        tabular_latex = '\n'.join((
                r'\begin{tabular}{l}',
                (20 * '\\multicolumn{1}{l}{foo} \\\\\n').strip(),
                r'\end{tabular}',
                r''
                ))

        self.assertEqual(self.convert(tabular_html), tabular_latex)

    def test_longtable_uses_endhead_for_ths(self):
        html = '\n'.join((
                r'<table>',
                r'<tr><th>heading</th></tr>',
                20 * r'<tr><td>content</td></tr>',
                r'</table>'))

        latex = self.convert(html, longtable=True)

        self.assertIn(r'\endhead', latex)

    def test_longtable_uses_endhead_for_thead_cells(self):
        html = '\n'.join((
                r'<table>',
                r' <thead>'
                r'  <tr><td>heading1</td></tr>',
                r'  <tr><td>heading2</td></tr>',
                r' </thead>',
                r' <tbody>',
                20 * r'<tr><td>content</td></tr>',
                r' </tbody>',
                r'</table>'))

        latex = self.convert(html, longtable=True)

        self.assertIn(r'\endhead', latex)

    def test_tabular_uses_no_endhead(self):
        html = '\n'.join((
                r'<table class="no-page-break">',
                r' <thead>',
                r'  <tr><th>heading</th></tr>',
                r' </thead>',
                r' <tbody>',
                r'  <tr><td>content</td></tr>',
                r' </tbody>',
                r'</table>'))

        latex = self.convert(html)

        self.assertNotIn(r'\endhead', latex)

    def test_simple_grid_css_class(self):
        html = '\n'.join((
                r'<table class="no-page-break border-grid">',
                r' <thead>',
                r'  <tr>',
                r'   <th>heading A</th>',
                r'   <th>heading B</th>',
                r'  </tr>',
                r' </thead>',
                r' <tbody>',
                r'  <tr>',
                r'   <td>content 1A</td>',
                r'   <td>content 1B</td>',
                r'  </tr>',
                r'  <tr>',
                r'   <td>content 2A</td>',
                r'   <td>content 2B</td>',
                r'  </tr>',
                r' </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{tabular}{|l|l|}',
                r'\hline',

                r'\multicolumn{1}{|l}{heading A} & ' + \
                    r'\multicolumn{1}{|l|}{heading B} \\',
                r'\hline',

                r'\multicolumn{1}{|l}{content 1A} & ' + \
                    r'\multicolumn{1}{|l|}{content 1B} \\',
                r'\hline',

                r'\multicolumn{1}{|l}{content 2A} & ' + \
                    r'\multicolumn{1}{|l|}{content 2B} \\',
                r'\hline',

                r'\end{tabular}',
                r''
                ))

        self.assertEqual(self.convert(html), latex)

    def test_complex_grid_css_class(self):
        html = '\n'.join((
                r'<table class="no-page-break listing">',
                r' <colgroup>',
                r'  <col width="50%" />'
                r'  <col width="25%" />'
                r'  <col width="25%" />'
                r' </colgroup>',
                r' <thead>',
                r'  <tr>',
                r'   <th colspan="3">heading</th>',
                r'  </tr>',
                r' </thead>',
                r' <tbody>',
                r'  <tr>',
                r'   <td>content 1A</td>',
                r'   <td rowspan="2">content 1/2 B</td>',
                r'   <td>content 1C</td>',
                r'  </tr>',
                r'  <tr>',
                r'   <td>content 2A</td>',
                r'   <td>content 2C</td>',
                r'  </tr>',
                r' </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\begin{tabular}{|p{0.5\linewidth}|p{0.25\linewidth}|' + \
                    'p{0.25\linewidth}|}',
                r'\hline',

                r'\multicolumn{3}{|p{1.0\linewidth}|}{heading} \\',
                r'\hline',

                r'\multicolumn{1}{|p{0.5\linewidth}|}{content 1A} & ' + \
                    r'\multirow{2}{0.25\textwidth}{content 1/2 B} & ' + \
                    r'\multicolumn{1}{|p{0.25\linewidth}|}{content 1C} \\',
                r'\hline',

                r'\multicolumn{1}{|p{0.5\linewidth}|}{content 2A} & ' + \
                    r' & '
                    r'\multicolumn{1}{|p{0.25\linewidth}|}{content 2C} \\',
                r'\hline',

                r'\end{tabular}',
                r''
                ))

        self.assertEqual(self.convert(html), latex)

    def test_border_classes(self):
        html = '\n'.join((
                r'<table class="no-page-break">',
                r' <thead>',
                r'  <tr>',
                r'   <th class="border-right">A1</th>',
                r'   <th class="border-top">B1</th>',
                r'   <th class="border-left border-bottom">C1</th>',
                r'  </tr>',
                r' </thead>',
                r' <tbody>',
                r'  <tr>',
                r'   <td class="border-right">A2</td>',
                r'   <td class="border-top border-bottom">B2</td>',
                r'   <td class="border-left border-bottom">C2</td>',
                r'  </tr>',
                r' </tbody>',
                r'</table>'
                ))


        latex = '\n'.join((
                r'\begin{tabular}{lll}',

                r'\cline{2-2}',
                r'\multicolumn{1}{l|}{A1} & ' + \
                    r'\multicolumn{1}{l}{B1} & ' + \
                    r'\multicolumn{1}{|l}{C1} \\',

                r'\cline{2-3}',
                r'\multicolumn{1}{l|}{A2} & ' + \
                    r'\multicolumn{1}{l}{B2} & ' + \
                    r'\multicolumn{1}{|l}{C2} \\',
                r'\cline{2-3}',

                r'\end{tabular}',
                r''
                ))

        self.assertEqual(self.convert(html), latex)

    def test_alignment_classes(self):
        html = '\n'.join((
                r'without width:',
                r'<table class="no-page-break">',
                r' <tr><td class="left">left</td></tr>',
                r' <tr><td class="center">center</td></tr>',
                r' <tr><td class="right">right</td></tr>',
                r'</table>',

                r'with width:',
                r'<table class="no-page-break">',
                r' <colgroup>',
                r'  <col width="100%" />',
                r' </colgroup>',
                r' <tr><td class="left">left</td></tr>',
                r' <tr><td class="center">center</td></tr>',
                r' <tr><td class="right">right</td></tr>',
                r' </tr>',
                r'</table>',
                ))

        latex = '\n'.join((
                r'without width: '
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{left} \\',
                r'\multicolumn{1}{c}{center} \\',
                r'\multicolumn{1}{r}{right} \\',
                r'\end{tabular}',

                r' with width: '
                r'\begin{tabular}{p{1.0\linewidth}}',
                r'\multicolumn{1}{p{1.0\linewidth}}{\raggedright left} \\',
                r'\multicolumn{1}{p{1.0\linewidth}}{' + \
                    r'\center\vspace{-1.5em}center} \\',
                r'\multicolumn{1}{p{1.0\linewidth}}{\raggedleft right} \\',
                r'\end{tabular}',
                r''
                ))

        self.assertEqual(self.convert(html, count=2), latex)

class TestLatexWidth(TestCase):

    def test_failing_convertion(self):
        with self.assertRaises(ValueError) as cm:
            table.LatexWidth.convert('123xy')

        self.assertEqual(
            str(cm.exception),
            'Could not convert string "123xy" to valid LatexWidth')

    def test_absolute_unit_width(self):
        width1 = table.LatexWidth.convert('100cm')
        self.assertEqual(width1.get(), r'100.0cm')
        self.assertEqual(str(width1), r'100.0cm')

        width2 = table.LatexWidth.convert('50.3cm')
        self.assertEqual(width2.get(), r'50.3cm')

        self.assertEqual((width1 + width2).get(),
                         r'150.3cm')

    def test_relative_width(self):
        width1 = table.LatexWidth.convert('10%')
        self.assertEqual(str(width1), r'0.1\linewidth')

        width2 = table.LatexWidth.convert('25%')
        self.assertEqual(str(width2), r'0.25\linewidth')

        self.assertEqual(str(width1 + width2),
                         r'0.35\linewidth')

    def test_defaults_to_em(self):
        width1 = table.LatexWidth.convert('50')
        self.assertEqual(str(width1), r'50.0em')

        width2 = table.LatexWidth.convert('20.0em')
        self.assertEqual(str(width1 + width2),
                         r'70.0em')

    def test_cm_is_converted_to_mm_when_summing(self):
        width1 = table.LatexWidth.convert('10.3cm')
        width2 = table.LatexWidth.convert('20.1mm')
        self.assertEqual(str(width1 + width2),
                         r'123.1mm')
        self.assertEqual(str(width2 + width1),
                         r'123.1mm')

    def test_fails_if_summing_with_non_width(self):
        width = table.LatexWidth.convert('10.3cm')

        with self.assertRaises(ValueError) as cm:
            width = width + 5

        self.assertEqual(
            str(cm.exception),
            'Cannot accumulate LatexWidth with int')

    def test_fails_if_unmatching_units(self):
        width1 = table.LatexWidth.convert('10em')
        width2 = table.LatexWidth.convert('20mm')

        with self.assertRaises(ValueError) as cm:
            width1 = width1 + width2

        self.assertEqual(
            str(cm.exception),
            'Cannot accumulate LatexWidths with different units (em, mm)')

    def test_fails_if_unmatching_types(self):
        width1 = table.LatexWidth.convert('10em')
        width2 = table.LatexWidth.convert('20%')

        with self.assertRaises(ValueError) as cm:
            width1 = width1 + width2

        self.assertEqual(
            str(cm.exception),
            'Cannot accumulate relative and absolute widths.')

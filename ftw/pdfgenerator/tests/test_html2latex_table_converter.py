from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.pdfgenerator.html2latex.subconverters import table
from ftw.pdfgenerator.testing import ZCML_WITH_SITE_LAYER
from ftw.testing import MockTestCase
from unittest2 import TestCase


class TestTableConverter(MockTestCase):

    layer = ZCML_WITH_SITE_LAYER

    def convert(self, *args, **kwargs):
        count = 1
        if 'count' in kwargs:
            count = kwargs['count']
            del kwargs['count']

        layout = self.mocker.mock()
        self.expect(layout.use_package('multirow')).count(count)
        self.expect(layout.use_package('multicol')).count(count)
        self.expect(layout.use_package('calc')).count(0, None)

        if 'use_packages' in kwargs:
            for pkg in kwargs['use_packages']:
                self.expect(layout.use_package(pkg)).count(count)
            del kwargs['use_packages']

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{\textbf{My Head}} \\',
                r'\multicolumn{1}{l}{My Body} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_table_converted_with_non_ascii(self):
        # Non-ASCII characters that *only* appear in table headings seem to
        # trip up BeautifulSoups charset sniffing.
        # This is a test case that would fail if BeautifulSoup was called
        # without an appropriate charset hint (fromEncoding='utf-8')
        html = '\n'.join((
                '<table>',
                '    <thead>',
                '        <tr><th>B\xc3\xa4rengraben</th></tr>',
                '    </thead><tbody>',
                '        <tr><td>My Body</td></tr>',
                '    </tbody>',
                '</table>'))

        latex = '\n'.join((
                '\\makeatletter\\@ifundefined{tablewidth}{\\newlength\\tablewidth}\\makeatother',
                '\\setlength\\tablewidth\\linewidth',
                '\\addtolength\\tablewidth{-2\\tabcolsep}',
                '\\renewcommand{\\arraystretch}{1.4}',
                '\\begin{tabular}{l}',
                '\\multicolumn{1}{l}{\\textbf{B\xc3\xa4rengraben}} \\\\',
                '\\multicolumn{1}{l}{My Body} \\\\',
                '\\end{tabular}\\\\',
                '\\vspace{4pt}',
                ''))

        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{ll}',
                r'\multicolumn{1}{l}{\textbf{headA}} & ' + \
                    r'\multicolumn{1}{l}{\textbf{headB}} \\',
                r'\multicolumn{1}{l}{1A} & \multicolumn{1}{l}{1B} \\',
                r'\multicolumn{1}{l}{2A} & \multicolumn{1}{l}{2B} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.3\tablewidth}p{0.7\tablewidth}}',

                r'\multicolumn{1}{p{0.3\tablewidth}}{test1} & '
                r'\multicolumn{1}{p{0.7\tablewidth}}{test2} \\',

                r'\multicolumn{1}{p{0.3\tablewidth}}{test3} & '
                r'\multicolumn{1}{p{0.7\tablewidth}}{test4} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.3\tablewidth}r}',

                r'\multicolumn{1}{p{0.3\tablewidth}}{test1} & '
                r'\multicolumn{1}{r}{test2} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.3\tablewidth}p{0.7\tablewidth}}',

                r'\multicolumn{1}{p{0.3\tablewidth}}{'
                r'\raggedleft test1} & \multicolumn{1}{'
                r'p{0.7\tablewidth}}{\raggedright test2} \\',

                r'\multicolumn{1}{p{0.3\tablewidth}}{\centering '
                r'test3} & \multicolumn{1}{p{0.7\tablewidth}}{test4} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_style_widths(self):

        html = '\n'.join((
                r'<table>',
                r'    <tbody>',
                r'        <tr>',
                r'            <td align="right" style="width:30%">test1</td>',
                r'            <td align="left" ' +
                r'style="color: red; width: 70%;">test2</td>',
                r'        </tr><tr>',
                r'            <td align="center">test3</td>',
                r'            <td>test4</td>',
                r'        </tr>',
                r'    </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{' +
                r'\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.3\tablewidth}p{0.7\tablewidth}}',

                r'\multicolumn{1}{p{0.3\tablewidth}}{'
                r'\raggedleft test1} & \multicolumn{1}{'
                r'p{0.7\tablewidth}}{\raggedright test2} \\',

                r'\multicolumn{1}{p{0.3\tablewidth}}{\centering '
                r'test3} & \multicolumn{1}{p{0.7\tablewidth}}{test4} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_style_widths_in_px(self):

        html = '\n'.join((
                r'<table>',
                r'    <tbody>',
                r'        <tr>',
                r'            <td align="right" style="width:30px">test1</td>',
                r'            <td align="left" ' +
                r'style="color: red; width: 70px;">test2</td>',
                r'        </tr><tr>',
                r'            <td align="center">test3</td>',
                r'            <td>test4</td>',
                r'        </tr>',
                r'    </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{' +
                r'\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{30.0em}p{70.0em}}',

                r'\multicolumn{1}{p{30.0em}}{'
                r'\raggedleft test1} & \multicolumn{1}{'
                r'p{70.0em}}{\raggedright test2} \\',

                r'\multicolumn{1}{p{30.0em}}{\centering '
                r'test3} & \multicolumn{1}{p{70.0em}}{test4} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)


    def test_caption_is_used(self):
        # The table caption is used and will be shown in the table index

        html = '\n'.join((
                r'<table>',
                r'    <caption>Testtabelle</caption>',
                r'    <tr><td>test</td></tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{' + \
                    r'\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',

                r'\begin{center}',
                r'\addtocounter{table}{1}',
                r'\addcontentsline{lot}{table}{' + \
                    r'\protect\numberline ' + \
                    r'{\thechapter.\arabic{table}}' + \
                    r'{\ignorespaces Testtabelle}' + \
                    r'}',
                r'Table \thechapter.\arabic{table}: Testtabelle',
                r'\end{center}',
                r'\vspace{-\baselineskip}',

                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{test} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_caption_not_listed(self):
        # It is also possible to add a caption whithout showing the table
        # in the table index by adding the css class "notListed"

        html = '\n'.join((
                r'<table class="notListed">',
                r'    <caption>NotIndexedCaption</caption>',
                r'    <tr><td>foo</td></tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{' + \
                    r'\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',

                r'\begin{center}',
                r'NotIndexedCaption',
                r'\end{center}',
                r'\vspace{-\baselineskip}',

                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{foo} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_caption_at_bottom(self):
        # For putting the caption to the bottom of table, just at the
        # <caption>-Tag at the bottom:

        html = '\n'.join((
                r'<table>',
                r'    <tr><td>foo</td></tr>',
                r'    <caption>My Table</caption>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{' + \
                    r'\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',

                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{foo} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',

                r'\vspace{-\baselineskip}',
                r'\begin{center}',
                r'\addtocounter{table}{1}',
                r'\addcontentsline{lot}{table}{' + \
                    r'\protect\numberline ' + \
                    r'{\thechapter.\arabic{table}}' + \
                    r'{\ignorespaces My Table}' + \
                    r'}',
                r'Table \thechapter.\arabic{table}: My Table',
                r'\end{center}',

                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_summary_as_caption(self):
        # Tinymce allows easily to put a <caption> tag at the top but not
        # at the bottom.
        # Therefore we use the "summary"-Attribute as bottom-caption.

        html = '\n'.join((
                r'<table summary="a quite simple table">',
                r'    <tr><td>foo</td></tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{' + \
                    r'\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',

                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{foo} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',

                r'\vspace{-\baselineskip}',
                r'\begin{center}',
                r'\addtocounter{table}{1}',
                r'\addcontentsline{lot}{table}{' + \
                    r'\protect\numberline ' + \
                    r'{\thechapter.\arabic{table}}' + \
                    r'{\ignorespaces a quite simple table}' + \
                    r'}',
                r'Table \thechapter.\arabic{table}: a quite simple table',
                r'\end{center}',

                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_summary_as_not_listed_caption(self):
        html = '\n'.join((
                r'<table class="notListed" summary="not listed table">',
                r'    <tr><td>foo</td></tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{' + \
                    r'\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',

                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{foo} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',

                r'\vspace{-\baselineskip}',
                r'\begin{center}',
                r'not listed table',
                r'\end{center}',

                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_multiple_tables(self):
        # Multiple tables should work as well

        html = r'<table><tr><td>test1</td></tr></table>' + \
            r'<table><tr><td>test2</td></tr></table>'

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength' + \
                    r'\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{test1} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r'\makeatletter\@ifundefined{tablewidth}{\newlength' + \
                    r'\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{test2} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html, count=2), latex)

    def test_convert_cell_html(self):
        # Table cells can contain other HTML which will be converted as well

        html = r'<table><tr><td><b>Hello</b> <i>World</i></td></tr></table>'

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{\textbf{Hello} \textit{World}} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_convert_other_html(self):
        # HTML around the Table should be converted as well

        html = '\n'.join((
                r'This <i>is</i> a <b>Table</b>:<br />',
                r'<table><tr><td>test</td></tr></table>',
                r'<b>yeah</b>'))

        latex = '\n'.join((
                r'This \textit{is} a \textbf{Table}:\\',
                r' \makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{test} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r' \textbf{yeah}'))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_htmlentities(self):
        # We should be able to use html entities (minidom has some
        # problems with htmlentites..)

        html = '\n'.join((
                r'<table>',
                r' <tr><td>2&gt;1</td></tr>',
                r' <tr><td>X&auml;Y</td></tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{2>1} \\',
                '\\multicolumn{1}{l}{X\xc3\xa4Y} \\\\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'    </tr><tr>',
                r'        <td colspan="3">all three</td>',
                r'    </tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-6\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.33\tablewidth}p{0.33\tablewidth}'
                r'p{0.34\tablewidth}}',

                r'\multicolumn{1}{p{0.33\tablewidth}}{one} & '
                r'\multicolumn{1}{p{0.33\tablewidth}}{two} & '
                r'\multicolumn{1}{p{0.34\tablewidth}}{three} \\',

                r'\multicolumn{2}{p{0.66\tablewidth+2\tabcolsep}}{one and two} & '
                r'\multicolumn{1}{p{0.34\tablewidth}}{three} \\',

                r'\multicolumn{3}{p{1.0\tablewidth+4\tabcolsep}}{all three} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.maxDiff = None
        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multirow{2}{0.5\tablewidth}{one} & \multicolumn{1}'
                r'{p{0.5\tablewidth}}{two} \\',

                r' & \multicolumn{1}{p{0.5\tablewidth}}{three} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength' + \
                    r'\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-10\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.25\tablewidth}p{0.25\tablewidth}' + \
                    r'p{0.25\tablewidth}p{0.25\tablewidth}l}',

                # row 1
                r'\multicolumn{1}{p{0.25\tablewidth}}{A1} & ' + \
                    r'\multirow{2}{0.25\tablewidth}{B1-B2} & ' + \
                    r'\multicolumn{1}{p{0.25\tablewidth}}{C1} & ' + \
                    r'\multicolumn{1}{p{0.25\tablewidth}}{D1} \\',

                # row 2
                r'\multicolumn{1}{p{0.25\tablewidth}}{A2} & ' + \
                    r' & '
                r'\multirow{2}{0.25\tablewidth}{C2-C3} & ' + \
                    r'\multicolumn{1}{p{0.25\tablewidth}}{D2} \\',

                # row 3
                r'\multicolumn{2}{p{0.5\tablewidth+2\tabcolsep}}{A3-B3} & '+\
                    r' & '
                r'\multicolumn{2}{l}{D3-E3} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.maxDiff = None
        self.assertMultiLineEqual(self.convert(html), latex)

    def test_rowspan_error_in_last_column(self):
        # Regression test that cells do not swap rows.

        html = '\n'.join((
                r'<table>',
                r'    <colspan>',
                r'        <col width="50%" />',
                r'        <col width="50%" />',
                r'    </colspan>',
                r'    <tbody>',
                r'        ',
                r'        <tr>',
                r'            <td>A</td>',
                r'            <td rowspan="2">2xB</td>',
                r'        </tr>',
                r'        <tr>',
                r'            <td>A</td>',
                r'        </tr>',
                r'        <tr>',
                r'            <td>A</td>',
                r'            <td>B</td>',
                r'        </tr>',
                r'        ',
                r'    </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{' + \
                    r'\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',
                r'\multicolumn{1}{p{0.5\tablewidth}}{A} &' + \
                    r' \multirow{2}{0.5\tablewidth}{2xB} \\',
                r'\multicolumn{1}{p{0.5\tablewidth}}{A} &  \\',
                r'\multicolumn{1}{p{0.5\tablewidth}}{A} &' + \
                    r' \multicolumn{1}{p{0.5\tablewidth}}{B} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.maxDiff = None
        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{|p{0.3\tablewidth}|p{0.7\tablewidth}|}',
                r'\hline',

                r'\multicolumn{1}{|p{0.3\tablewidth}}{test1} & '
                r'\multicolumn{1}{|p{0.7\tablewidth}|}{test2} \\',

                r'\hline',

                r'\multicolumn{1}{|p{0.3\tablewidth}}{test3} & '
                r'\multicolumn{1}{|p{0.7\tablewidth}|}{test4} \\',

                r'\hline',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength' + \
                    r'\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'hello\newline world} & ' + \
                    r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'foo\newline \newline bar} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'foo} & ' + \
                    r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'bar} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(tabular_html), tabular_latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{longtable}{l}',
                (40 * '\\multicolumn{1}{l}{foo} \\\\\n').strip(),
                r'\end{longtable}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(longtable_html,
                                               use_packages=['longtable']),
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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{longtable}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'foo} & ' + \
                    r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'bar} \\',

                r'\end{longtable}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(longtable_html,
                                               use_packages=['longtable']),
                                  longtable_latex)

    def test_tabular_environment_enforcable_by_cssclass(self):
        tabular_html = '\n'.join((
                r'<table class="no-page-break">',
                20 * r'<tr><td>foo</td></tr>',
                r'</table>',
                ))

        tabular_latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{l}',
                (20 * '\\multicolumn{1}{l}{foo} \\\\\n').strip(),
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(tabular_html), tabular_latex)

    def test_longtable_uses_endhead_for_ths(self):
        html = '\n'.join((
                r'<table>',
                r'<tr><th>heading</th></tr>',
                20 * r'<tr><td>content</td></tr>',
                r'</table>'))

        latex = self.convert(html, use_packages=['longtable'])

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

        latex = self.convert(html, use_packages=['longtable'])

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{|l|l|}',
                r'\hline',

                r'\multicolumn{1}{|l}{\textbf{heading A}} & ' + \
                    r'\multicolumn{1}{|l|}{\textbf{heading B}} \\',
                r'\hline',

                r'\multicolumn{1}{|l}{content 1A} & ' + \
                    r'\multicolumn{1}{|l|}{content 1B} \\',
                r'\hline',

                r'\multicolumn{1}{|l}{content 2A} & ' + \
                    r'\multicolumn{1}{|l|}{content 2B} \\',
                r'\hline',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_complex_grid_css_class(self):
        html = '\n'.join((
                r'<table class="no-page-break grid">',
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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-6\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{|p{0.5\tablewidth}|p{0.25\tablewidth}|' + \
                    r'p{0.25\tablewidth}|}',
                r'\hline',

                r'\multicolumn{3}{|p{1.0\tablewidth+4\tabcolsep}|}{' + \
                    r'\textbf{heading}} \\',
                r'\hline',

                r'\multicolumn{1}{|p{0.5\tablewidth}|}{content 1A} & ' + \
                    r'\multirow{2}{0.25\tablewidth}{content 1/2 B} & ' + \
                    r'\multicolumn{1}{|p{0.25\tablewidth}|}{content 1C} \\',
                r'\cline{1-1}\cline{3-3}',

                r'\multicolumn{1}{|p{0.5\tablewidth}|}{content 2A} & ' + \
                    r' & '
                r'\multicolumn{1}{|p{0.25\tablewidth}|}{content 2C} \\',
                r'\hline',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.maxDiff = None
        self.assertMultiLineEqual(self.convert(html), latex)

    def test_border_rowspan_collapse(self):
        html = '\n'.join((
                r'<table class="no-page-break">',
                r' <colgroup>',
                r'  <col width="25%" />'
                r'  <col width="25%" />'
                r'  <col width="25%" />'
                r'  <col width="25%" />'
                r' </colgroup>',
                r' <tbody>',
                r'  <tr>',
                r'   <td rowspan="2">1A</td>',
                r'   <td>content 1B</td>',
                r'   <td rowspan="2" class="border-right border-left">' + \
                    r'content 1/2 C</td>',
                r'   <td>content 1D</td>',
                r'  </tr>',
                r'  <tr>',
                r'   <td>content 2B</td>',
                r'   <td>content 2D</td>',
                r'  </tr>',
                r' </tbody>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-8\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.25\tablewidth}p{0.25\tablewidth}' + \
                    r'p{0.25\tablewidth}p{0.25\tablewidth}}',

                r'\multirow{2}{0.25\tablewidth}{1A} & ' + \
                    r'\multicolumn{1}{p{0.25\tablewidth}|}{content 1B} & ' + \
                    r'\multirow{2}{0.25\tablewidth}{content 1/2 C} & ' + \
                    r'\multicolumn{1}{|p{0.25\tablewidth}}{content 1D} \\',

                r' & ' + \
                    r'\multicolumn{1}{p{0.25\tablewidth}|}{content 2B} & ' + \
                    r' & '
                r'\multicolumn{1}{|p{0.25\tablewidth}}{content 2D} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_listing_css_class(self):
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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-6\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.25\tablewidth}' + \
                    r'p{0.25\tablewidth}}',
                r'\hline',

                r'\multicolumn{3}{p{1.0\tablewidth+4\tabcolsep}}{' + \
                    r'\textbf{heading}} \\',
                r'\hline',

                r'\multicolumn{1}{p{0.5\tablewidth}}{content 1A} & ' + \
                    r'\multirow{2}{0.25\tablewidth}{content 1/2 B} & ' + \
                    r'\multicolumn{1}{p{0.25\tablewidth}}{content 1C} \\',
                r'\cline{1-1}\cline{3-3}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{content 2A} & ' + \
                    r' & '
                r'\multicolumn{1}{p{0.25\tablewidth}}{content 2C} \\',
                r'\hline',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_vertical_css_class_makes_first_column_bold(self):
        html = '\n'.join((
                r'<table class="no-page-break vertical">',
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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-6\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.25\tablewidth}' + \
                    r'p{0.25\tablewidth}}',

                r'\multicolumn{3}{p{1.0\tablewidth+4\tabcolsep}}{' + \
                    r'\textbf{heading}} \\',

                r'\multicolumn{1}{p{0.5\tablewidth}}' + \
                    r'{\textbf{content 1A}} & ' + \
                    r'\multirow{2}{0.25\tablewidth}{content 1/2 B} & ' + \
                    r'\multicolumn{1}{p{0.25\tablewidth}}{content 1C} \\',

                r'\multicolumn{1}{p{0.5\tablewidth}}' + \
                    r'{\textbf{content 2A}} & ' + \
                    r' & ' + \
                    r'\multicolumn{1}{p{0.25\tablewidth}}{content 2C} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.maxDiff = None
        self.assertMultiLineEqual(self.convert(html), latex)

    def test_colspan_without_width(self):
        html = '\n'.join((
                r'<table>',
                r'<tr>',
                r'<td>foo</td>',
                r'<td>bar</td>',
                r'</tr><tr>',
                r'<td colspan="2">baz</td>',
                r'</tr>',
                r'</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{' + \
                    r'\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{ll}',

                r'\multicolumn{1}{l}{foo} & ' + \
                    r'\multicolumn{1}{l}{bar} \\',
                r'\multicolumn{2}{l}{baz} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_border_classes(self):
        html = '\n'.join((
                r'<table class="no-page-break">',
                r' <tbody>',
                r'  <tr>',
                r'   <td class="border-right">A1</td>',
                r'   <td class="border-top">B1</td>',
                r'   <td class="border-left border-bottom">C1</td>',
                r'  </tr>',
                r'  <tr>',
                r'   <td class="border-right">A2</td>',
                r'   <td class="border-top border-bottom">B2</td>',
                r'   <td class="border-left border-bottom">C2</td>',
                r'  </tr>',
                r' </tbody>',
                r'</table>'
                ))


        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-6\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
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

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

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
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{l}',
                r'\multicolumn{1}{l}{left} \\',
                r'\multicolumn{1}{c}{center} \\',
                r'\multicolumn{1}{r}{right} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',

                r' with width: '
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-2\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{1.0\tablewidth}}',
                r'\multicolumn{1}{p{1.0\tablewidth}}{\raggedright left} \\',
                r'\multicolumn{1}{p{1.0\tablewidth}}{' + \
                    r'\centering center} \\',
                r'\multicolumn{1}{p{1.0\tablewidth}}{\raggedleft right} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html, count=2), latex)

    def test_indent2_class(self):
        html = '\n'.join((
                r'<table>',
                r'  <tr>',
                r'    <td width="50%" class="indent2">foo</td>',
                r'    <td width="50%">bar</td>',
                r'  </tr>',
                r'</table>',
                ))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'\hangindent 0.2cm\hspace{0.2cm} foo} & ' + \
                    r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'bar} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_indent10_class(self):
        html = '\n'.join((
                r'<table>',
                r'  <tr>',
                r'    <td width="50%" class="indent10">foo</td>',
                r'    <td width="50%">bar</td>',
                r'  </tr>',
                r'</table>',
                ))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'\hangindent 1cm\hspace{1cm} foo} & ' + \
                    r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'bar} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_bold_class(self):
        html = '\n'.join((
                r'<table>',
                r'  <tr>',
                r'    <td width="50%" class="bold">foo</td>',
                r'    <td width="50%" class="bold indent10">bar</td>',
                r'  </tr>',
                r'</table>',
                ))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'\textbf{foo}} & ' + \
                    r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'\hangindent 1cm\hspace{1cm} \textbf{bar}} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_grey_class(self):
        html = '\n'.join((
                r'<table>',
                r'  <tr>',
                r'    <td width="50%" class="grey">foo</td>',
                r'    <td width="50%">bar</td>',
                r'  </tr>',
                r'</table>',
                ))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'\textcolor{gray}{foo}} & ' + \
                    r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'bar} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html, use_packages=['xcolor']),
                                  latex)

    def test_footnotesize_class(self):
        html = '\n'.join((
                r'<table>',
                r'  <tr>',
                r'    <td width="50%" class="footnotesize">foo</td>',
                r'    <td width="50%">bar</td>',
                r'  </tr>',
                r'</table>',
                ))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'\footnotesize foo} & ' + \
                    r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'bar} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_scriptsize_class(self):
        html = '\n'.join((
                r'<table>',
                r'  <tr>',
                r'    <td width="50%" class="scriptsize">foo</td>',
                r'    <td width="50%">bar</td>',
                r'  </tr>',
                r'</table>',
                ))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'\scriptsize foo} & ' + \
                    r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'bar} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_ragged_and_style_order(self):
        # \raggedright should be first, the \textbf
        html = '\n'.join((
                r'<table>',
                r'  <tr>',
                r'    <td width="50%" class="bold right">foo</td>',
                r'    <td width="50%">bar</td>',
                r'  </tr>',
                r'</table>',
                ))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.5\tablewidth}p{0.5\tablewidth}}',

                r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'\raggedleft \textbf{foo}} & ' + \
                    r'\multicolumn{1}{p{0.5\tablewidth}}{' + \
                    r'bar} \\',

                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.assertMultiLineEqual(self.convert(html), latex)

    def test_more_cols_than_cells(self):
        # Regression test for when there are more <col> tags than <td> tags per row.
        html = '\n'.join((
                '<table class="plain" style="width: 100%;">',
                '  <colgroup>',
                '    <col width="17%" />',
                '    <col width="41%" />',
                '    <col width="35%" />',
                '  </colgroup>',
                '  <tbody>',
                '    <tr>',
                '      <th style="width: 30%;">Foo</th>',
                '      <th style="width: 70%;">Bar</th>',
                '    </tr>',
                '  </tbody>',
                '</table>'))

        latex = '\n'.join((
                r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
                r'\setlength\tablewidth\linewidth',
                r'\addtolength\tablewidth{-4\tabcolsep}',
                r'\renewcommand{\arraystretch}{1.4}',
                r'\begin{tabular}{p{0.17\tablewidth}p{0.41\tablewidth}}',
                r'\multicolumn{1}{p{0.3\tablewidth}}{\textbf{Foo}} & \multicolumn{1}{p{0.7\tablewidth}}{\textbf{Bar}} \\',
                r'\end{tabular}\\',
                r'\vspace{4pt}',
                r''
                ))

        self.maxDiff = None
        self.assertMultiLineEqual(self.convert(html), latex)

    def test_vertical_th_isnt_repeated(self):
        html = '\n'.join((
                r'<table class="plain" style="width: 100%;">',
                r'  <colgroup>',
                r'    <col width="17%" />',
                r'    <col width="41%" />',
                r'    <col width="35%" />',
                r'  </colgroup>',
                r'  <thead>',
                r'    <tr>',
                r'      <td style="width: 30%;">Foo</th>',
                r'      <td style="width: 70%;">Bar</th>',
                r'    </tr>',
                r'   </thead>',
                r'   <tbody>',
                20 * r'    <tr><th style="width: 30%;">Foo</th><td style="width: 70%;">Batz</td></tr>',
                r'  </tbody>',
                r'</table>'))

        latex_list = [
            r'\makeatletter\@ifundefined{tablewidth}{\newlength\tablewidth}\makeatother',
            r'\setlength\tablewidth\linewidth',
            r'\addtolength\tablewidth{-4\tabcolsep}',
            r'\renewcommand{\arraystretch}{1.4}',
            r'\begin{longtable}{p{0.17\tablewidth}p{0.41\tablewidth}}',
            r'\multicolumn{1}{p{0.3\tablewidth}}{\textbf{Foo}} & \multicolumn{1}{p{0.7\tablewidth}}{\textbf{Bar}} \\',
            r'\endhead',
        ]
        for counter in range(20):
            latex_list.append(r'\multicolumn{1}{p{0.3\tablewidth}}{\textbf{Foo}} & \multicolumn{1}{p{0.7\tablewidth}}{Batz} \\')
        latex_list.append(r'\end{longtable}\\')
        latex_list.append(r'\vspace{4pt}')
        latex_list.append(r'')
        latex = '\n'.join(latex_list)

        self.maxDiff = None
        self.assertMultiLineEqual(self.convert(html, use_packages=['longtable']), latex)


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
        self.assertEqual(str(width1), r'0.1\tablewidth')

        width2 = table.LatexWidth.convert('25%')
        self.assertEqual(str(width2), r'0.25\tablewidth')

        self.assertEqual(str(width1 + width2),
                         r'0.35\tablewidth')

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

    def test_px_is_the_same_as_no_measure_unit(self):
        width_px = table.LatexWidth.convert('50px')
        width_no = table.LatexWidth.convert('50')

        self.assertEqual(str(width_no), str(width_px))

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


class TestParseHTMLStyleAttribute(TestCase):

    def test_empty(self):
        self.assertEqual(table.parse_html_style_attribute(''), {})

    def test_none(self):
        self.assertEqual(table.parse_html_style_attribute(None), {})

    def test_single_argument(self):
        self.assertEqual(table.parse_html_style_attribute('width: 10'),
                         {'width': '10'})

        self.assertEqual(table.parse_html_style_attribute('width:10;'),
                         {'width': '10'})

        self.assertEqual(table.parse_html_style_attribute('width : 10 ;'),
                         {'width': '10'})

        self.assertEqual(table.parse_html_style_attribute('width : 10 ;;'),
                         {'width': '10'})

    def test_multiple_arguments(self):
        self.assertEqual(table.parse_html_style_attribute(
                'width:10;height:5'),
                         {'width': '10',
                          'height': '5'})

        self.assertEqual(table.parse_html_style_attribute(
                'width : 10 ; height : 5 ;'),
                         {'width': '10',
                          'height': '5'})

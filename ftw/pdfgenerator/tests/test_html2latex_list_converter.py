from ftw.pdfgenerator.html2latex.subconverters import listing
from ftw.pdfgenerator.tests.base import SubconverterTestBase


class TestListConverter(SubconverterTestBase):

    def test_converter_is_default(self):
        self.assertIn(
            listing.ListConverter,
            self.converter.get_default_subconverters())

    def test_converts_lists_with_win_paths(self):
        self.assertEqual(
            self.convert('<ul><li>O:\\foo\\bar\\baz</li></ul>'),
            '\n\\begin{itemize}\n'
            '\\item O:\\textbackslash foo\\textbackslash bar\\textbackslash baz\n'
            '\\end{itemize}\n')

        self.assertEqual(
            self.convert('<ul><li>One</li><li>Two</li><li>Three</li></ul>'),
            '\n\\begin{itemize}\n\\item One\n\\item Two\n\\item Three\n'
            '\\end{itemize}\n')

        self.assertEqual(
            self.convert('<ol>\n<li>First</li>\n<li>Second</li>\n'
                         '<li>Third</li>\n</ol>'),
            '\n\\begin{enumerate}\n\\item First\n\\item Second\n'
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
                '',
                '\\begin{enumerate}',
                '\\item a',
                '\\item b         ',
                '\\begin{enumerate}',
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

        latex = '\n'.join((r'',
                           r'\begin{itemize}',
                           r'\item a',
                           r'\item b         ',
                           r'\begin{itemize}',
                           r'\item ba',
                           r'\item bb',
                           r'\end{itemize}',
                           r'\item c',
                           r'\end{itemize}',
                           r''))

        self.assertEqual(self.convert(html), latex)

    def test_list_values_are_converted(self):
        html = '<ul><li>This is <b>important</b>!</ul>'
        latex = '\n'.join((r'',
                           r'\begin{itemize}',
                           r'\item This is \textbf{important}!',
                           r'\end{itemize}',
                           r''))

        self.assertEqual(self.convert(html), latex)

    def test_list_with_attributes_matches(self):
        html = '<ul style="list-style-type: square;" class="simple">' + \
            '<li>Any text</li></ul>'
        latex = '\n'.join((r'',
                           r'\begin{itemize}',
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
                r'',
                r'\begin{itemize}',
                r'\item foo',
                r'\item bar',
                r'\end{itemize}',
                r'',
                r'\textbf{foobar}',
                r'',
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
                '',
                '<ul>',
                '<li>foo</li>',
                'bar',
                '</ul>',
                'baz',
                '<dl>',
                '<dt>foo</dt>',
                '<dd>bar</dd>',
                'baz',
                '</dl>'))

        latex = '\n'.join((
                r'',
                r'\begin{itemize}',
                r'\item foo',
                r'bar',
                r'\end{itemize}',
                r' baz ',
                r'\begin{description}',
                r'\item[foo] bar',
                r'baz',
                r'\end{description}',
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
                r'',
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
                r'',
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

    def test_bad_nested_unordered_listings(self):
        html = '\n'.join((
                'foo',
                '<ul>',
                '<ul>',
                '<li>bar</li>',
                '</ul>',
                '</ul>',
                'bar'))

        latex = 'foo \n\\begin{itemize}\n\\item bar\n\\end{itemize}\n bar'

        self.assertEqual(self.convert(html), latex)

    def test_bad_nested_definition_listings(self):
        html = '\n'.join((
                'foo',
                '<dl>',
                '<dl>',
                '<dt>bar</dt>',
                '<dd>baz</dd>',
                '</dl>',
                '</dl>',
                'bar'))

        latex = 'foo \n\\begin{description}\n' + \
            '\\item[bar] baz\n\\end{description}\n bar'

        self.assertEqual(self.convert(html), latex)

    def test_outer_nesting(self):
        html = '\n'.join(('<ul>',
                          '    <li>a</li>',
                          '    <ul>',
                          '        <li>ba</li>',
                          '        <li>bb</li>',
                          '    </ul>',
                          '    <li>b</li>',
                          '    <dl>',
                          '        <dt>foo</dt>',
                          '        <dd>bar</dd>',
                          '        <ol>',
                          '            <li>baz</li>',
                          '        </ol>',
                          '    </dl>',
                          '    <li>c</li>',
                          '</ul>'))

        latex = '\n'.join((r'',
                           r'\begin{itemize}',
                           r'\item a',
                           r'',
                           r'\begin{itemize}',
                           r'\item ba',
                           r'\item bb',
                           r'\end{itemize}',
                           r'\item b',
                           r'',
                           r'\begin{description}',
                           r'\item[foo] bar',
                           r'',
                           r'\begin{enumerate}',
                           r'\item baz',
                           r'\end{enumerate}',
                           r'\end{description}',
                           r'\item c',
                           r'\end{itemize}',
                           r''))

        self.assertEqual(self.convert(html), latex)

    def test_limit_list_nesting_to_4(self):
        """LaTeX allows a maximum list nesting of 4, we need to flatten
        further nested lists into level 4.
        """
        html = '\n'.join((
                r'<ul><li>one</li>',
                r'  <ul><li>two</li>',
                r'    <ul><li>three</li>',
                r'      <ul><li>four</li>',
                r'        <ul><li>five</li>',
                r'          <ul><li>six</li>',
                r'          </ul>',
                r'        </ul>',
                r'      </ul>',
                r'    </ul>',
                r'  </ul>',
                r'</ul>',
                ))

        latex = '\n'.join((
                r'',
                r'\begin{itemize}',
                r'\item one',
                r'',
                r'\begin{itemize}',
                r'\item two',
                r'',
                r'\begin{itemize}',
                r'\item three',
                r'',
                r'\begin{itemize}',
                r'\item four',
                r'\item five',
                r'\item six',
                r'\end{itemize}',
                r'\end{itemize}',
                r'\end{itemize}',
                r'\end{itemize}',
                r'',
                ))
        self.assertEqual(self.convert(html), latex)

    def test_ul_does_not_fail_on_empty_item(self):
        html = '\n'.join((
                '<ul>',
                '<li>foo</li>',
                '<li></li>',
                '<li>bar</li>',
                '</ul>'))

        latex = '\n'.join((
                r'',
                r'\begin{itemize}',
                r'\item foo',
                r'\item bar',
                r'\end{itemize}',
                r'',
                ))

        self.assertEqual(self.convert(html), latex)

    def test_dl_does_not_fail_on_empty_item(self):
        html = '\n'.join((
                '<dl>',
                '<dt>foo</dt>',
                '<dd></dd>',
                '<dt></dt>',
                '<dd>bar</dd>',
                '</dl>'))

        latex = '\n'.join((
                r'',
                r'\begin{description}',
                r'\item[foo] ',
                r'\item[] bar',
                r'\end{description}',
                r'',
                ))

        self.assertEqual(self.convert(html), latex)

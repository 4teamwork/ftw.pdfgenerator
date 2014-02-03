from ftw.pdfgenerator.html2latex.subconverters import textformatting
from ftw.pdfgenerator.tests.base import SubconverterTestBase



class TestTextformattingConverter(SubconverterTestBase):

    def test_converter_is_default(self):
        self.assertIn(
            textformatting.Textformatting,
            self.converter.get_default_subconverters())

    def test_find_bracket_range(self):
        text = 'foo {bar} baz'
        span = (4, 9)
        self.assertEqual(
            textformatting.find_bracket_range(text),
            span)
        self.assertEqual(text[span[0]:span[1]], '{bar}')

        self.assertEqual(
            textformatting.find_bracket_range(
                'one {two {three {four }}} five'),
            (4, 25))

        self.assertEqual(
            textformatting.find_bracket_range('} foo {bar} baz'),
            (6, 11))

        self.assertEqual(
            textformatting.find_bracket_range('1 } 2 { 3'),
            None)

    def test_newline_in_bold_command(self):
        # "\textbf{X\n\n}" is not allowed, use "\textbf{X\\}"
        self.assertEqual(
            self.convert(r'<p><b>foo<br /> <br /></b></p>'),
            r'\textbf{foo\\\\}')

    def test_newline_in_bold_command2(self):
        # "\textbf{X\n\nY}" is not allowed, use "\textbf{X\\Y}"
        self.assertEqual(
            self.convert(r'<p><b>foo<br /> <br />bar</b></p>'),
            r'\textbf{foo\\\\bar}')

    def test_newline_in_bold_command3(self):
        # "\textbf{\n\nY}" is not allowed, use "\textbf{\\Y}"
        self.assertEqual(
            self.convert(r'<b><br /> <br />bar</b>' * 2),
            r'\textbf{\\\\bar}' * 2)

    def test_newline_in_emph_command(self):
        # "\emph{X\n\n}" is not allowed, use "\emph{X\\}"
        self.assertEqual(
            self.convert(r'foo <u>bar<br /> <br /></u> baz'),
            r'foo \emph{bar\\\\} baz')

    def test_newline_in_emph_command2(self):
        # "\emph{X\n\nY}" is not allowed, use "\emph{X\\Y}"
        self.assertEqual(
            self.convert(r'<u>foo<br /> <br />bar</u>'),
            r'\emph{foo\\\\bar}')

    def test_newline_in_emph_command3(self):
        # "\emph{\n\nY}" is not allowed, use "\emph{\\Y}"
        self.assertEqual(
            self.convert(r'<u><br /> <br />bar</u>' * 2),
            r'\emph{\\\\bar}' * 2)

    def test_newline_in_italic_command(self):
        # "\textit{X\n\n}" is not allowed, use "\textit{X\\}"
        self.assertEqual(
            self.convert(r'<p><i>foo<br /> <br /></i></p>'),
            r'\textit{foo\\\\}')

    def test_newline_in_italic_command2(self):
        # "\textit{X\n\nY}" is not allowed, use "\textit{X\\Y}"
        self.assertEqual(
            self.convert(r'<p><i>foo<br /> <br />bar</i></p>'),
            r'\textit{foo\\\\bar}')

    def test_newline_in_italic_command3(self):
        # "\textit{\n\nY}" is not allowed, use "\textit{\\Y}"
        self.assertEqual(
            self.convert(r'<i><br /> <br />bar</i>' * 2),
            r'\textit{\\\\bar}' * 2)

    def test_newline_in_combined_italic_and_bold_command(self):
        # "\textit{*\n\n*}" is not allowed, use "\textit{*\\*}"
        # "\textbf{*\n\n*}" is not allowed, use "\textbf{*\\*}"
        self.assertEqual(
            self.convert(r'<i>foo'
                         r'<b>bar</b><br /> <br />'
                         r'<u>baz</u><br /> <br />'
                         r'</i>'),
            r'\textit{foo\textbf{bar}\\\\\emph{baz}\\\\}')

        self.assertEqual(
            self.convert(r'<b>foo<i>bar</i><br /> <br /></b>'),
            r'\textbf{foo\textit{bar}\\\\}')

    def test_newline_only_in_textish_environments_changed(self):
        self.assertEqual(
            self.convert(r'<p><i>foo</i><br /><br ><p><p>bar</p>' * 2),
            ('\\textit{foo}\n\nbar\n\n' * 2).strip())

    def test_multiple_textish_environments(self):
        self.assertEqual(
            self.convert(
                r'<p>one <b>two</b> three</p><p>four <b>five</b></p>'),
            'one \\textbf{two} three\n\nfour \\textbf{five}')

# -*- coding: latin-1 -*-


from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.pdfgenerator.html2latex.subconverters import textformatting
from ftw.pdfgenerator.html2latex.subconverters import url
from unittest2 import TestCase


class BasicConverter(HTML2LatexConverter):
    """A HTML2LatexConverter where subconverters are disabled.
    """

    def get_default_subconverters(self):
        return [url.URLConverter,
                textformatting.Textformatting]


class TestBasicPatterns(TestCase):

    def setUp(self):
        super(TestBasicPatterns, self).setUp()

        self.converter = BasicConverter(
            context=object(),
            request=object(),
            layout=object())

        self.convert = self.converter.convert

    def test_common_text_formatting(self):
        self.assertEqual(self.convert('Hello <b>World</b>!'),
                         'Hello \\textbf{World}!')

        self.assertEqual(self.convert('Hello <strong>World</strong>!'),
                         'Hello \\textbf{World}!')

        self.assertEqual(self.convert('Hello <u>World</u>!'),
                         'Hello \\emph{World}!')

        self.assertEqual(self.convert('Hello <u id="foo">World</u>!'),
                         'Hello \\emph{World}!')

        self.assertEqual(self.convert('Hello <em>World</em>!'),
                         'Hello \\emph{World}!')

        self.assertEqual(self.convert('Hello <em id="foo">World</em>!'),
                         'Hello \\emph{World}!')

        self.assertEqual(self.convert('Hello <i>World</i>!'),
                         'Hello \\textit{World}!')

        self.assertEqual(self.convert('Hello <i id="foo">World</i>!'),
                         'Hello \\textit{World}!')

        self.assertEqual(self.convert('capacity: 55 m<sup>3</sup>'),
                         'capacity: 55 m\\textsuperscript{3}')

    def test_remove_unused_tags(self):
        self.assertEqual(self.convert('<span>Hello World!</span>'),
                         'Hello World!')

        self.assertEqual(self.convert('Hallo <b></b> Welt <asdf></asdf>'),
                         'Hallo  Welt')

        # Remove image maps
        self.assertEqual(self.convert(
                'foo\n'
                '<map name="ImageMap1">\n'

                '<area shape="rect" coords="158, 128, 276, 194"'
                ' href="http://localhost//bar-2005-2015-31.12.2009"'
                ' target="_self" alt="Bar">\n'

                '<area shape="rect" coords="170, 333, 287, 398"'
                ' href="http://localhost//foo" target="_self" alt="foo">\n'

                '<area shape="rect" coords="310, 137, 421, 179"'
                ' href="http://localhost//foo-bar" target="_self"'
                ' alt="Foo B������r">\n'

                '<area shape="rect" coords="36, 168, 123, 208" '
                'href="./a/url" target="_blank" alt="Something">\n'
                '</map>\n'
                'bar'),
                         'foo       bar')

    def test_headings(self):
        self.assertEqual(self.convert('<h1>My Heading</h1>'),
                         '\\section{My Heading}')

        self.assertEqual(self.convert('<h2 align="right">Subheading</h2>'),
                         '\\subsection{Subheading}')

    def test_quotation_marks(self):
        self.assertEqual(
            self.convert('Hello "World" that\'s &quot;my&quot; test..'),
            'Hello "`World"\' that\'s "`my"\' test..')

        self.assertEqual(
            self.convert('Hello "World" that\'s &quot;my&quot;, test..'),
            'Hello "`World"\' that\'s "`my"\', test..')

        self.assertEqual(self.convert('"Hello" World'),
                         '"`Hello"\' World')

        self.assertEqual(self.convert('Bar "foo (1)" blubb'),
                         'Bar "`foo (1)"\' blubb')

        self.assertEqual('"`Hello World"\'',
                         self.convert('<p>"Hello World"</p>'))

    def test_quotation_marks2(self):
        self.assertEqual(self.convert('foo &quot;<b>bar</b>&quot; baz'),
                         'foo "`\\textbf{bar}"\' baz')

    def test_quotation_marks3(self):
        self.assertEqual(self.convert('foo <b>&quot;bar&quot;</b> baz'),
                         'foo \\textbf{"`bar"\'} baz')

    def test_whitespace(self):
        self.assertEqual(self.convert('U\x0bV\x0cW\r\nX\nY\rZ'),
                         'U V W X Y Z')

        # Use short whitespace (\,) for abbreviation:
        self.assertEqual(self.convert('x e.g. y').strip(),
                         'x e.\,g. y')

        self.assertEqual(self.convert('x e. g. y').strip(),
                         'x e.\,g. y')

        self.assertEqual(self.convert('test i. d. r. foo').strip(),
                         'test i.\,d.\,r. foo')

        # test trimming newlines
        self.assertEqual(self.convert('<b>eins</b>'),
                         '\\textbf{eins}')

        self.assertEqual(self.convert('<b>zwei</b><br />zwei'),
                         '\\textbf{zwei}\\\\\nzwei')

        self.assertEqual(self.convert('<b>drei<br /></b>'),
                         '\\textbf{drei\\\\\n}')

        self.assertEqual(self.convert('<b>vier<br />\n</b>'),
                         '\\textbf{vier\\\\\n }')

        self.assertEqual(self.convert('<b>fuenf<br />\n</b><br />'),
                         '\\textbf{fuenf\\\\\n }')

        self.assertEqual(self.convert('<b>sechs<br />\n</b>sechs<br />'),
                         '\\textbf{sechs\\\\\n }sechs')

        self.assertEqual(self.convert('<strong>&quot;sieben&quot;<br />\n'
                                      '</strong><br />'),
                         '\\textbf{"`sieben"\'\\\\\n }')

    def test_abbreviations_are_not_breakable(self):
        self.maxDiff = None

        self.assert_convertions({
                'S. 5': 'S.~5',
                'S. 15': 'S.~15',
                'S. 17. Bar': 'S.~17. Bar',
                'Sa 2': 'Sa 2',

                'Abs. 5': 'Abs.~5',
                'Abs. 15': 'Abs.~15',
                'Abs. 17. Bar': 'Abs.~17. Bar',
                'Absx 2': 'Absx 2',

                '5 m2': '5~m2',
                '17 m2': '17~m2',
                'a5 m2': 'a5~m2',

                'Art. 5': 'Art.~5',
                'Art. 15': 'Art.~15',
                'Art. 17. Bar': 'Art.~17. Bar',
                'Arta 1': 'Arta 1',

                'SR 5': 'SR~5',
                'SR 15': 'SR~15',
                'SR 17. Bar': 'SR~17. Bar',
                })

    def test_paragraphs_and_newlines(self):
        self.assertEqual(self.convert('Hello<br><br>World'),
                         'Hello\n\nWorld')

        self.assertEqual(self.convert('Hello<br /> \n  <br/>World'),
                         'Hello\n\nWorld')

        self.assertEqual(self.convert('<p>Hello</p><p>World</p>'),
                         'Hello\n\nWorld')

        self.assertEqual(self.convert('Hello<br>World'),
                         'Hello\\\\\nWorld')

        self.assertEqual(self.convert('Carriage<br />Return'),
                         'Carriage\\\\\nReturn')

        self.assertEqual(
            self.convert('<p>Hello</p><p>World</p><p></p><p></p><p></p>'),
            'Hello\n\nWorld')

        self.assertEqual(
            self.convert('<p><span style="font-weight: bold;">Mitglieder'
                         '</span><br />Name1<br />Name2<br /></p>').strip(),
            '\n'.join((
                    r'\textbf{Mitglieder}\\',
                    r'Name1\\',
                    r'Name2')))

        self.assertEqual(self.convert('<p><strong><br />Text</strong></p>'),
                         r'\textbf{Text}')

    def test_curly_bracket_spaces(self):
        # If there is no space at left of the curly brackets, there will
        # not be any space in the displayed text (PDF), but in HTML it
        # is (with the bold-tag in HTML the browser displays a bold space).

        self.assertEqual(self.convert('text<b> bold text</b>'),
                         'text \\textbf{bold text}')

        self.assertEqual(self.convert('text<strong> bold text</strong>'),
                         'text \\textbf{bold text}')

        self.assertEqual(self.convert('te<b>X</b>t'),
                         'te\\textbf{X}t')

        self.assertEqual(self.convert('a<em> b</em> c'),
                         'a \\emph{b} c')

        self.assertEqual(self.convert('a<u> b</u> c'),
                         'a \\emph{b} c')

        self.assertEqual(self.convert('a<i> b</i> c'),
                         'a \\textit{b} c')

        self.assertEqual(self.convert('a <i>b</i> c'),
                         'a \\textit{b} c')

        self.assertEqual(self.convert('a<i>b</i>c'),
                         'a\\textit{b}c')

    def test_links(self):
        # Blank links should be stripped
        self.assertEqual(
            self.convert('<a href="about:blank">Something</a>'),
            'Something')

    def test_fckeditor_compatibility(self):
        # FCKEditor doesnt use <b> nor <strong> but <span>
        # with style-attribute:
        self.assertEqual(
            self.convert('Hello <span style="font-weight: bold;">my</span>'
                         ' world'),
            'Hello \\textbf{my} world')

        self.assertEqual(
            self.convert('<span style="font-weight: bold;">test</span>'),
            '\\textbf{test}')

        self.assertEqual(
            self.convert('<span style="font-weight: bold">test</span>'),
            '\\textbf{test}')

    def test_asterisks(self):
        """Asterisks (*) needs to be defined using the \ast command,
        which does only work properly in math-environments ($$).
        """
        self.assertEqual(self.convert('foo * bar'),
                         r'foo $\ast$ bar')

    def test_sepcial_characters(self):
        self.assertEqual(self.convert('!#$%&amp;\'()+-./02345'),
                         "!\\#\\$\\%\\&'()+-./02345")

        self.assertEqual(self.convert('6789:;&lt;=&gt;?@ABCDEFGHI'),
                         '6789:;<=>?@ABCDEFGHI')

        self.assertEqual(self.convert('JKLMNOPQRSTUVWXYZ[]^'),
                         'JKLMNOPQRSTUVWXYZ[]\\^{}')

        self.assertEqual(self.convert('_`abcdefghiklmnopqr'),
                         '\\_`abcdefghiklmnopqr')

        self.assertEqual(self.convert('stuvwxyz{|}~'),
                         'stuvwxyz\\{|\\}\\~{}')

        # XXX: fix those tests: maybe decode to unicode or use propper utf8
        # char escaping.
        self.assertEqual(
            self.convert('&euro;&lsquo;&rsquo;&rsquo;'
                         '&ldquo;&rdquo;&ndash;&mdash;'),
            '\euro{}‘’’�'
            '��”–—')

        self.assertEqual(
            self.convert(
                '&iexcl;&cent;&pound;&curren;&sect;&uml;&copy;&ordf;'),
            '¡\cent{}£\currency{}\S¨©ª')

        self.assertEqual(
            self.convert('&laquo;&reg;&macr;&sup2;&sup3;&acute;&micro;'),
            '«®¯²³´µ')

        self.assertEqual(
            self.convert('&middot;&cedil;&sup1;&ordm;&raquo;&iquest;'),
            '·¸¹º»¿')

        self.assertEqual(
            self.convert('ÀÁÂÃÅÆÇÈÉ'),
            'ÀÁÂÃÅÆÇÈÉ')

        self.assertEqual(
            self.convert('ÊËÌÍÎÏÐÑÒÓ'),
            'ÊËÌÍÎÏÐÑÒÓ')

        self.assertEqual(
            self.convert('ÔÕÖØÙÚÛÜÝ'),
            'ÔÕÖØÙÚÛÜÝ')

        self.assertEqual(
            self.convert('Þßàáâãäåæç'),
            'Þßàáâãäåæç')

        self.assertEqual(
            self.convert('èéêëìíîïðñ'),
            'èéêëìíîïðñ')

        self.assertEqual(
            self.convert('òóôõöøùúû'),
            'òóôõöøùúû')

        self.assertEqual(
            self.convert('üüýþÿŒœ&sbquo;&bdquo;'),
            'üüýþÿŒœ‚„')

        self.assertEqual(self.convert('&divide;'), '$\\div$')
        self.assertEqual(self.convert('&times;'), '$\\times$')
        self.assertEqual(self.convert('&frac12;'), '$\\frac12$')
        self.assertEqual(self.convert('&frac34;'), '$\\frac34$')
        self.assertEqual(self.convert('&frac14;'), '$\\frac14$')
        self.assertEqual(self.convert('&para;'), '\\P')
        self.assertEqual(self.convert('&deg;'), '$\\circ$')
        self.assertEqual(self.convert('&plusmn;'), '$\\pm$')
        self.assertEqual(self.convert('&not;'), '\\ensuremath{\\lnot}')
        self.assertEqual(self.convert('&hellip;'), '$\\dots$')
        self.assertEqual(self.convert('&trade;'), '™')
        self.assertEqual(self.convert('&bull;'), '•')
        self.assertEqual(self.convert('&rarr;'), '$\\rightarrow$')
        self.assertEqual(self.convert('&rArr;'), '$\\Rightarrow$')
        self.assertEqual(self.convert('&hArr;'), '⇔')
        self.assertEqual(self.convert('&asymp;'), '$\\approx$')

        # unsupported sepcial chars:
        self.assertEqual(
            self.convert('&yen;&brvbar;‛&diams;►'),
            '')

    def test_hyphenation_characters(self):
        self.assertEqual(
            self.convert('ergo\xc2\xadnomic'), 'ergo"-nomic')
        self.assertEqual(
            self.convert('ergo&shy;nomic'), 'ergo"-nomic')

    def test_non_breakable_hyphens_before_comma(self):
        self.assert_convertions({
                'foo-, bar': 'foo"~, bar',
                'foo- bar': 'foo"= bar'})

    def test_remove_css(self):
        self.assertEqual(self.convert(
                'hello\n'
                '<style type="text/css">\n'
                '    <!--\n'
                '        body {\n'
                '            background-color: red;\n'
                '        }\n'
                '    /-->\n'
                '</style>\n'
                'world').strip(),
                         'hello  world')

    def test_various(self):
        # Delimiter Symbol must should be escaped in LaTeX-Style:
        self.assertEqual(
            self.convert('Unterstützungs- und Hilfsberichte').strip(),
            'Unterstützungs"= und Hilfsberichte')

        # We don't like linebreaks between numbers and a %-character,
        # so we prevent it
        self.assertEqual(self.convert('101.5 %').strip(),
                         '101.5\,\%')

        # But maybe we use a %-character in the text:
        self.assertEqual(self.convert('we use %-characters').strip(),
                         'we use \%-characters')

        # Test some german stuff
        self.assertEqual(
            self.convert('foo lic.iur. foo Dr.iur. foo z.B. foo '
                         'z. B. foo').strip(),
            'foo lic.\,iur. foo Dr.\,iur. foo z.\,B. foo z.\,B. foo')

        # We dont want spaces to break:
        self.assertEqual(self.convert('1. Januar 2008').strip(),
                         '1.~Januar 2008')

        self.assertEqual(self.convert('4. Feb. 2008').strip(),
                         '4.~Feb. 2008')

        # Usually we want to have a small space after a paragraph character,
        # if it is followed by a integer (\S is the LaTeX command for
        # the §-character):
        self.assertEqual(self.convert('foo §1 foo § 2 foo').strip(),
                         'foo \S\,1 foo \S\,2 foo')

        # Backslashes
        self.assertEqual(self.convert(r'C:\Programs\foo').strip(),
                         r'C:\textbackslash Programs\textbackslash foo')

    def test_removes_nonbreaking_spaces(self):
        # Non break spaces are evil. In HTML they are usually not used the
        # way they should be used in LaTeX, so we replace them with spaces.
        self.assertEqual(self.convert(u'Hello\xa0World'),
                         'Hello World')

    def test_tinymce_paste(self):
        # cleanup problem with many _mcePaste divs.
        html = '\n'.join((
                '<p> </p>',
                '<div id="_mcePaste">one</div>',
                '<div id="_mcePaste"></div>',
                '<div id="_mcePaste">two</div>',
                '<div id="_mcePaste"></div>',
                '<div id="_mcePaste">three</div>',
                '<div id="_mcePaste"></div>',
                '<div id="_mcePaste">four</div>',
                '<div id="_mcePaste"></div>',
                '<div id="_mcePaste">five</div>',
                '<p>six<br />seven<br />eight</p>'))

        self.assertNotIn('div', self.convert(html))
        self.assertNotIn('mcePaste', self.convert(html))
        self.assertNotIn('<', self.convert(html))
        self.assertNotIn('>', self.convert(html))

    def test_repeat_bug(self):
        # bug was to pass re.DOTALL (which is 16) to the re.sub() function,
        # which caused to only replace the first 16 matches.
        times = 20
        html = ('<b>foo</b> ' * times).strip()
        latex = (r'\textbf{foo} ' * times).strip()

        result = self.convert(html)

        self.assertEqual(len(result), len(latex))
        self.assertEqual(result, latex)

    def test_callout_is_not_too_greedy(self):
        # Bug caused the callout pattern to be too greedy, which resulted
        # in swallowed content.
        html = '<p>foo</p> <p class="callout">bar</p> <p>baz</p>'
        result = self.convert(html)

        self.assertIn('foo', result)
        self.assertIn('bar', result)
        self.assertIn('baz', result)

    def test_no_space_after_italic(self):
        # we used to have a little space after italic text when using the
        # old school syntax {\em }. But since the new syntax \emph{} does
        # this automatically, we don't insert it manually anymore.
        html = 'foo <em>bar</em> baz'
        latex = r'foo \emph{bar} baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <u>bar</u> baz'
        latex = r'foo \emph{bar} baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <i>bar</i> baz'
        latex = r'foo \textit{bar} baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo (<em>bar</em>) baz'
        latex = r'foo (\emph{bar}) baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo (<u>bar</u>) baz'
        latex = r'foo (\emph{bar}) baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo (<i>bar</i>) baz'
        latex = r'foo (\textit{bar}) baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <em>bar</em>-baz'
        latex = r'foo \emph{bar}-baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <u>bar</u>-baz'
        latex = r'foo \emph{bar}-baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <i>bar</i>-baz'
        latex = r'foo \textit{bar}-baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <em>bar</em>'
        latex = r'foo \emph{bar}'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <u>bar</u>'
        latex = r'foo \emph{bar}'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <i>bar</i>'
        latex = r'foo \textit{bar}'
        self.assertEqual(self.convert(html), latex)

    def test_utf8_math_charaters(self):
        self.assertEqual(self.convert(u'\u22a5'.encode('utf-8')),
                         r'$\perp$')

        self.assertEqual(self.convert(u'\u2264'.encode('utf-8')),
                         r'$\leq$')

        self.assertEqual(self.convert(u'\u2216'.encode('utf-8')),
                         r'$\setminus$')

        self.assertEqual(self.convert(u'\u2283'.encode('utf-8')),
                         r'$\supset$')

        self.assertEqual(self.convert(u'\u211c'.encode('utf-8')),
                         r'$\Re$')

        self.assertEqual(self.convert(u'\u2197'.encode('utf-8')),
                         r'$\nearrow$')

        self.assertEqual(self.convert(u'\u221a'.encode('utf-8')),
                         r'$\surd$')

        self.assertEqual(self.convert(u'\xbd'.encode('utf-8')),
                         r'$\frac12$')

        self.assertEqual(self.convert(u'\u2153'.encode('utf-8')),
                         r'$\frac13$')

        self.assertEqual(self.convert(u'\xbc'.encode('utf-8')),
                         r'$\frac14$')

        self.assertEqual(self.convert(u'\u2155'.encode('utf-8')),
                         r'$\frac15$')

        self.assertEqual(self.convert(u'\u2159'.encode('utf-8')),
                         r'$\frac16$')

        self.assertEqual(self.convert(u'\u215b'.encode('utf-8')),
                         r'$\frac18$')

        self.assertEqual(self.convert(u'\u2229'.encode('utf-8')),
                         r'$\cap$')

        self.assertEqual(self.convert(u'\u03a3'.encode('utf-8')),
                         r'$\Sigma$')

        self.assertEqual(self.convert(u'\u03a8'.encode('utf-8')),
                         r'$\Psi$')

        self.assertEqual(self.convert(u'\u03a9'.encode('utf-8')),
                         r'$\Omega$')

        self.assertEqual(self.convert(u'\u2205'.encode('utf-8')),
                         r'$\emptyset$')

        self.assertEqual(self.convert(u'\u22c3'.encode('utf-8')),
                         r'$\bigcup$')

        self.assertEqual(self.convert(u'\u2190'.encode('utf-8')),
                         r'$\leftarrow$')

        self.assertEqual(self.convert(u'\u227a'.encode('utf-8')),
                         r'$\prec$')

        self.assertEqual(self.convert(u'\u2297'.encode('utf-8')),
                         r'$\otimes$')

        self.assertEqual(self.convert(u'\u2135'.encode('utf-8')),
                         r'$\aleph$')

        self.assertEqual(self.convert(u'\u22ef'.encode('utf-8')),
                         r'$\cdots$')

        self.assertEqual(self.convert(u'\u2245'.encode('utf-8')),
                         r'$\cong$')

        self.assertEqual(self.convert(u'\u2261'.encode('utf-8')),
                         r'$\equiv$')

        self.assertEqual(self.convert(u'\u226a'.encode('utf-8')),
                         r'$\ll$')

        self.assertEqual(self.convert(u'\u22c6'.encode('utf-8')),
                         r'$\star$')

        self.assertEqual(self.convert(u'\u2260'.encode('utf-8')),
                         r'$\neq$')

        self.assertEqual(self.convert(u'\u03b1'.encode('utf-8')),
                         r'$\alpha$')

        self.assertEqual(self.convert(u'\u2210'.encode('utf-8')),
                         r'$\amalg$')

        self.assertEqual(self.convert(u'\u228e'.encode('utf-8')),
                         r'$\uplus$')

        self.assertEqual(self.convert(u'\u03ba'.encode('utf-8')),
                         r'$\kappa$')

        self.assertEqual(self.convert(u'\u03c3'.encode('utf-8')),
                         r'$\sigma$')

        self.assertEqual(self.convert(u'\u039b'.encode('utf-8')),
                         r'$\Lambda$')

        self.assertEqual(self.convert(u'\u222a'.encode('utf-8')),
                         r'$\cup$')

        self.assertEqual(self.convert(u'\u03bb'.encode('utf-8')),
                         r'$\lambda$')

        self.assertEqual(self.convert(u'\u0398'.encode('utf-8')),
                         r'$\Theta$')

        self.assertEqual(self.convert(u'\u221c'.encode('utf-8')),
                         r'$\sqrt4$')

        self.assertEqual(self.convert(u'\u2240'.encode('utf-8')),
                         r'$\wr$')

        self.assertEqual(self.convert(u'\u2118'.encode('utf-8')),
                         r'$\wp$')

        self.assertEqual(self.convert(u'\u221b'.encode('utf-8')),
                         r'$\sqrt3$')

        self.assertEqual(self.convert(u'\xac'.encode('utf-8')),
                         r'\ensuremath{\lnot}')

        self.assertEqual(self.convert(u'\u2293'.encode('utf-8')),
                         r'$\sqcap$')

        self.assertEqual(self.convert(u'\u03f1'.encode('utf-8')),
                         r'$\varrho$')

        self.assertEqual(self.convert(u'\u03b2'.encode('utf-8')),
                         r'$\beta$')

        self.assertEqual(self.convert(u'\u22a3'.encode('utf-8')),
                         r'$\dashv$')

        self.assertEqual(self.convert(u'\u2265'.encode('utf-8')),
                         r'$\geq$')

        self.assertEqual(self.convert(u'\u2199'.encode('utf-8')),
                         r'$\searrow$')

        self.assertEqual(self.convert(u'\u2664'.encode('utf-8')),
                         r'$\spadesuit$')

        self.assertEqual(self.convert(u'\u2021'.encode('utf-8')),
                         r'$\ddag$')

        self.assertEqual(self.convert(u'\u220f'.encode('utf-8')),
                         r'$\prod$')

        self.assertEqual(self.convert(u'\u2156'.encode('utf-8')),
                         r'$\frac25$')

        self.assertEqual(self.convert(u'\u2154'.encode('utf-8')),
                         r'$\frac23$')

        self.assertEqual(self.convert(u'\u22a4'.encode('utf-8')),
                         r'$\bot$')

        self.assertEqual(self.convert(u'\u21d1'.encode('utf-8')),
                         r'$\Uparrow$')

        self.assertEqual(self.convert(u'\u2194'.encode('utf-8')),
                         r'$\leftrightarrow$')

        self.assertEqual(self.convert(u'\u03c8'.encode('utf-8')),
                         r'$\psi$')

        self.assertEqual(self.convert(u'\u21c0'.encode('utf-8')),
                         r'$\rightharpoonup$')

        self.assertEqual(self.convert(u'\u2219'.encode('utf-8')),
                         r'$\bullet$')

        self.assertEqual(self.convert(u'\u03d5'.encode('utf-8')),
                         r'$\varphi$')

        self.assertEqual(self.convert(u'\u03db'.encode('utf-8')),
                         r'$\varsigma$')

        self.assertEqual(self.convert(u'\u2284'.encode('utf-8')),
                         r'$\not\subset$')

        self.assertEqual(self.convert(u'\u2206'.encode('utf-8')),
                         r'$\Delta$')

        self.assertEqual(self.convert(u'\xb0'.encode('utf-8')),
                         r'$\circ$')

        self.assertEqual(self.convert(u'\u03c5'.encode('utf-8')),
                         r'$\upsilon$')

        self.assertEqual(self.convert(u'\u03c7'.encode('utf-8')),
                         r'$\chi$')

        self.assertEqual(self.convert(u'\u2250'.encode('utf-8')),
                         r'$\doteq$')

        self.assertEqual(self.convert(u'\u2191'.encode('utf-8')),
                         r'$\uparrow$')

        self.assertEqual(self.convert(u'\u222d'.encode('utf-8')),
                         r'$\iiint$')

        self.assertEqual(self.convert(u'\u266d'.encode('utf-8')),
                         r'$\flat$')

        self.assertEqual(self.convert(u'\u03a6'.encode('utf-8')),
                         r'$\Phi$')

        self.assertEqual(self.convert(u'\u03f5'.encode('utf-8')),
                         r'$\epsilon$')

        self.assertEqual(self.convert(u'\u03d6'.encode('utf-8')),
                         r'$\varpi$')

        self.assertEqual(self.convert(u'\u22c2'.encode('utf-8')),
                         r'$\bigcap$')

        self.assertEqual(self.convert(u'\u03a0'.encode('utf-8')),
                         r'$\Pi$')

        self.assertEqual(self.convert(u'\u2020'.encode('utf-8')),
                         r'$\dag$')

        self.assertEqual(self.convert(u'\u2217'.encode('utf-8')),
                         r'$\ast$')

        self.assertEqual(self.convert(u'\u21a6'.encode('utf-8')),
                         r'$\mapsto$')

        self.assertEqual(self.convert(u'\u03b8'.encode('utf-8')),
                         r'$\theta$')

        self.assertEqual(self.convert(u'\u222e'.encode('utf-8')),
                         r'$\oint$')

        self.assertEqual(self.convert(u'\u2295'.encode('utf-8')),
                         r'$\oplus$')

        self.assertEqual(self.convert(u'\u22c4'.encode('utf-8')),
                         r'$\diamond$')

        self.assertEqual(self.convert(u'\u2113'.encode('utf-8')),
                         r'$\ell$')

        self.assertEqual(self.convert(u'\u2213'.encode('utf-8')),
                         r'$\mp$')

        self.assertEqual(self.convert(u'\u2207'.encode('utf-8')),
                         r'$\nabla$')

        self.assertEqual(self.convert(u'\u220c'.encode('utf-8')),
                         r'$\not\ni$')

        self.assertEqual(self.convert(u'\u2298'.encode('utf-8')),
                         r'$\oslash$')

        self.assertEqual(self.convert(u'\u222c'.encode('utf-8')),
                         r'$\iint$')

        self.assertEqual(self.convert(u'\u22c5'.encode('utf-8')),
                         r'$\cdot$')

        self.assertEqual(self.convert(u'\u2111'.encode('utf-8')),
                         r'$\Im$')

        self.assertEqual(self.convert(u'\xb1'.encode('utf-8')),
                         r'$\pm$')

        self.assertEqual(self.convert(u'\u03c0'.encode('utf-8')),
                         r'$\pi$')

        self.assertEqual(self.convert(u'\u2287'.encode('utf-8')),
                         r'$\supseteq$')

        self.assertEqual(self.convert(u'\u0393'.encode('utf-8')),
                         r'$\Gamma$')

        self.assertEqual(self.convert(u'\u03c4'.encode('utf-8')),
                         r'$\tau$')

        self.assertEqual(self.convert(u'\u2299'.encode('utf-8')),
                         r'$\odot$')

        self.assertEqual(self.convert(u'\u21aa'.encode('utf-8')),
                         r'$\hookrightarrow$')

        self.assertEqual(self.convert(u'\u2294'.encode('utf-8')),
                         r'$\sqcup$')

        self.assertEqual(self.convert(u'\u22a8'.encode('utf-8')),
                         r'$\models$')

        self.assertEqual(self.convert(u'\u21d2'.encode('utf-8')),
                         r'$\Rightarrow$')

        self.assertEqual(self.convert(u'\u22c0'.encode('utf-8')),
                         r'$\bigwedge$')

        self.assertEqual(self.convert(u'\u03c9'.encode('utf-8')),
                         r'$\omega$')

        self.assertEqual(self.convert(u'\u215c'.encode('utf-8')),
                         r'$\frac38$')

        self.assertEqual(self.convert(u'\u221d'.encode('utf-8')),
                         r'$\propto$')

        self.assertEqual(self.convert(u'\u266f'.encode('utf-8')),
                         r'$\sharp$')

        self.assertEqual(self.convert(u'\u03bc'.encode('utf-8')),
                         r'$\mu$')

        self.assertEqual(self.convert(u'\u2157'.encode('utf-8')),
                         r'$\frac35$')

        self.assertEqual(self.convert(u'\xbe'.encode('utf-8')),
                         r'$\frac34$')

        self.assertEqual(self.convert(u'\u220a'.encode('utf-8')),
                         r'$\in$')

        self.assertEqual(self.convert(u'\u03b5'.encode('utf-8')),
                         r'$\varepsilon$')

        self.assertEqual(self.convert(u'\u03b6'.encode('utf-8')),
                         r'$\zeta$')

        self.assertEqual(self.convert(u'\u03b7'.encode('utf-8')),
                         r'$\eta$')

        self.assertEqual(self.convert(u'\u2244'.encode('utf-8')),
                         r'$\not\simeq$')

        self.assertEqual(self.convert(u'\u2158'.encode('utf-8')),
                         r'$\frac45$')

        self.assertEqual(self.convert(u'\u2200'.encode('utf-8')),
                         r'$\forall$')

        self.assertEqual(self.convert(u'\xd7'.encode('utf-8')),
                         r'$\times$')

        self.assertEqual(self.convert(u'\u2026'.encode('utf-8')),
                         r'$\dots$')

        self.assertEqual(self.convert(u'\u2262'.encode('utf-8')),
                         r'$\not\equiv$')

        self.assertEqual(self.convert(u'\u2196'.encode('utf-8')),
                         r'$\nwarrow$')

        self.assertEqual(self.convert(u'\u2227'.encode('utf-8')),
                         r'$\wedge$')

        self.assertEqual(self.convert(u'\u03c1'.encode('utf-8')),
                         r'$\rho$')

        self.assertEqual(self.convert(u'\u2666'.encode('utf-8')),
                         r'$\diamondsuit$')

        self.assertEqual(self.convert(u'\u220d'.encode('utf-8')),
                         r'$\ni$')

        self.assertEqual(self.convert(u'\u2192'.encode('utf-8')),
                         r'$\rightarrow$')

        self.assertEqual(self.convert(u'\u039e'.encode('utf-8')),
                         r'$\Xi$')

        self.assertEqual(self.convert(u'\u03b9'.encode('utf-8')),
                         r'$\iota$')

        self.assertEqual(self.convert(u'\u03bd'.encode('utf-8')),
                         r'$\nu$')

        self.assertEqual(self.convert(u'\xf7'.encode('utf-8')),
                         r'$\div$')

        self.assertEqual(self.convert(u'\xa7'.encode('utf-8')),
                         r'\S')

        self.assertEqual(self.convert(u'\u03d1'.encode('utf-8')),
                         r'$\vartheta$')

        self.assertEqual(self.convert(u'\u03c6'.encode('utf-8')),
                         r'$\phi$')

        self.assertEqual(self.convert(u'\u22a2'.encode('utf-8')),
                         r'$\vdash$')

        self.assertEqual(self.convert(u'\u2209'.encode('utf-8')),
                         r'$\notin$')

        self.assertEqual(self.convert(u'\u2296'.encode('utf-8')),
                         r'$\ominus$')

        self.assertEqual(self.convert(u'\u210f'.encode('utf-8')),
                         r'$\hbar$')

        self.assertEqual(self.convert(u'\u2220'.encode('utf-8')),
                         r'$\angle$')

        self.assertEqual(self.convert(u'\u227b'.encode('utf-8')),
                         r'$\succ$')

        self.assertEqual(self.convert(u'\u221e'.encode('utf-8')),
                         r'$\infty$')

        self.assertEqual(self.convert(u'\u03be'.encode('utf-8')),
                         r'$\xi$')

        self.assertEqual(self.convert(u'\u2665'.encode('utf-8')),
                         r'$\heartsuit$')

        self.assertEqual(self.convert(u'\u2249'.encode('utf-8')),
                         r'$\not\approx$')

        self.assertEqual(self.convert(u'\xb6'.encode('utf-8')),
                         r'\P')

        self.assertEqual(self.convert(u'\u21d0'.encode('utf-8')),
                         r'$\Leftarrow$')

        self.assertEqual(self.convert(u'\u2228'.encode('utf-8')),
                         r'$\vee$')

        self.assertEqual(self.convert(u'\u03b3'.encode('utf-8')),
                         r'$\gamma$')

        self.assertEqual(self.convert(u'\u2195'.encode('utf-8')),
                         r'$\updownarrow$')

        self.assertEqual(self.convert(u'\u224d'.encode('utf-8')),
                         r'$\asymp$')

        self.assertEqual(self.convert(u'\u222b'.encode('utf-8')),
                         r'$\int$')

        self.assertEqual(self.convert(u'\u223c'.encode('utf-8')),
                         r'$\sim$')

        self.assertEqual(self.convert(u'\u2667'.encode('utf-8')),
                         r'$\clubsuit$')

        self.assertEqual(self.convert(u'\u215e'.encode('utf-8')),
                         r'$\frac78$')

        self.assertEqual(self.convert(u'\u21a9'.encode('utf-8')),
                         r'$\hookleftarrow$')

        self.assertEqual(self.convert(u'\u2193'.encode('utf-8')),
                         r'$\downarrow$')

        self.assertEqual(self.convert(u'\u226b'.encode('utf-8')),
                         r'$\gg$')

        self.assertEqual(self.convert(u'\u22c1'.encode('utf-8')),
                         r'$\bigvee$')

        self.assertEqual(self.convert(u'\u226d'.encode('utf-8')),
                         r'$\not\asymp$')

        self.assertEqual(self.convert(u'\u21d5'.encode('utf-8')),
                         r'$\Updownarrow$')

        self.assertEqual(self.convert(u'\u03b4'.encode('utf-8')),
                         r'$\delta$')

        self.assertEqual(self.convert(u'\u21bc'.encode('utf-8')),
                         r'$\leftharpoonup$')

        self.assertEqual(self.convert(u'\u2243'.encode('utf-8')),
                         r'$\simeq$')

        self.assertEqual(self.convert(u'\u2225'.encode('utf-8')),
                         r'$\parallel$')

        self.assertEqual(self.convert(u'\u215d'.encode('utf-8')),
                         r'$\frac58$')

        self.assertEqual(self.convert(u'\u215a'.encode('utf-8')),
                         r'$\frac56$')

        self.assertEqual(self.convert(u'\u2248'.encode('utf-8')),
                         r'$\approx$')

        self.assertEqual(self.convert(u'\u21c1'.encode('utf-8')),
                         r'$\rightharpoondown$')

        self.assertEqual(self.convert(u'\u2202'.encode('utf-8')),
                         r'$\partial$')

        self.assertEqual(self.convert(u'\u2286'.encode('utf-8')),
                         r'$\subseteq$')

        self.assertEqual(self.convert(u'\u21cc'.encode('utf-8')),
                         r'$\rightleftharpoons$')

        self.assertEqual(self.convert(u'\u2223'.encode('utf-8')),
                         r'$\mid$')

        self.assertEqual(self.convert(u'\u215f'.encode('utf-8')),
                         r'$\frac14$')

        self.assertEqual(self.convert(u'\u21bd'.encode('utf-8')),
                         r'$\leftharpoondown$')

        self.assertEqual(self.convert(u'\u21d3'.encode('utf-8')),
                         r'$\Downarrow$')

        self.assertEqual(self.convert(u'\u22c8'.encode('utf-8')),
                         r'$\bowtie$')

        self.assertEqual(self.convert(u'\u266e'.encode('utf-8')),
                         r'$\natural$')

        self.assertEqual(self.convert(u'\u22ee'.encode('utf-8')),
                         r'$\vdots$')

        self.assertEqual(self.convert(u'\u2211'.encode('utf-8')),
                         r'$\sum$')

        self.assertEqual(self.convert(u'\u2285'.encode('utf-8')),
                         r'$\not\supset$')

        self.assertEqual(self.convert(u'\u2282'.encode('utf-8')),
                         r'$\subset$')

    def test_swiss_currency_with_dash(self):
        self.assertEqual([
                'Fr.~0.--',
                'Fr.~123.--',
                'Fr.~45.--',
                'Fr.~67.--',
                'Fr. .-',

                ], [
                self.convert('Fr. 0.-'),
                self.convert('Fr. 123.-'),
                self.convert('Fr. 45.--'),
                self.convert('Fr. 67.\xe2\x80\x93'),
                self.convert('Fr. .-'),
                ])

    def test_html_comments_are_removed(self):
        samples = (
            ('<!-- foo -->', ''),
            ('<!-- foo --> bar <!-- baz -->', 'bar'),
            ('<!-- <b>foo</b> -->', ''),
            ('<!--foo-->', ''),
            ('<!--[foo]-->', ''),
            ('<!--[if x]> <b>bar</b> <![endif]-->', ''),
            )

        self.assertEquals(
            [item[1] for item in samples],
            [self.convert(item[0]).strip() for item in samples])

    def test_cleans_up_bad_word_comments(self):
        input = '\n'.join((
                '<!--[if gte mso 9]><xml>',
                '<o:OfficeDocumentSettings>',
                '<o:TargetScreenSize>800x600</o:TargetScreenSize>',
                '</o:OfficeDocumentSettings>',
                '</xml><![endif]-->',

                ))

        self.assertEqual('', self.convert(input).strip())

    def test_hyphenation_infos_are_added_to_urls(self):
        self.assertEqual(
            self.convert(
                'x http://foo.ch/bar y'),
            'x http://foo.ch""/bar y')

        self.assertEqual(
            self.convert(
                'x https://user@pass:domain.com/foo/bar.html?param=true#anchor y'),
            'x https://user@pass:domain.com""/foo""/bar.html?param=true\\#anchor y')

    def assert_convertions(self, input_expected):
        input_output = {}

        for input, _expected in input_expected.items():
            input_output[input] = self.convert(input).strip()

        self.assertEqual(input_expected, input_output)

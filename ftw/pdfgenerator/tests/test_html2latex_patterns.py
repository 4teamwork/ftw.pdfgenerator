# -*- coding: latin-1 -*-


from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from unittest2 import TestCase


class BasicConverter(HTML2LatexConverter):
    """A HTML2LatexConverter where subconverters are disabled.
    """

    def get_default_subconverters(self):
        return []


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
                         'Hello {\\bf World}!')

        self.assertEqual(self.convert('Hello <strong>World</strong>!'),
                         'Hello {\\bf World}!')

        self.assertEqual(self.convert('Hello <u>World</u>!'),
                         'Hello {\\em World}\\/!')

        self.assertEqual(self.convert('Hello <u id="foo">World</u>!'),
                         'Hello {\\em World}\\/!')

        self.assertEqual(self.convert('Hello <em>World</em>!'),
                         'Hello {\\em World}\\/!')

        self.assertEqual(self.convert('Hello <em id="foo">World</em>!'),
                         'Hello {\\em World}\\/!')

        self.assertEqual(self.convert('Hello <i>World</i>!'),
                         'Hello {\\it World}\\/!')

        self.assertEqual(self.convert('Hello <i id="foo">World</i>!'),
                         'Hello {\\it World}\\/!')

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

    def test_whitespace(self):
        self.assertEqual(self.convert('W\r\nX\nY\rZ'),
                         'W X Y Z')

        # Use short whitespace (\,) for abbreviation:
        self.assertEqual(self.convert('x e.g. y').strip(),
                         'x e.\,g. y')

        self.assertEqual(self.convert('x e. g. y').strip(),
                         'x e.\,g. y')

        self.assertEqual(self.convert('test i. d. r. foo').strip(),
                         'test i.\,d.\,r. foo')

        # test trimming newlines
        self.assertEqual(self.convert('<b>eins</b>'),
                         '{\\bf eins}')

        self.assertEqual(self.convert('<b>zwei</b><br />zwei'),
                         '{\\bf zwei}\\\\\nzwei')

        self.assertEqual(self.convert('<b>drei<br /></b>'),
                         '{\\bf drei\\\\\n}')

        self.assertEqual(self.convert('<b>vier<br />\n</b>'),
                         '{\\bf vier\\\\\n }')

        self.assertEqual(self.convert('<b>fuenf<br />\n</b><br />'),
                         '{\\bf fuenf\\\\\n }')

        self.assertEqual(self.convert('<b>sechs<br />\n</b>sechs<br />'),
                         '{\\bf sechs\\\\\n }sechs')

        self.assertEqual(self.convert('<strong>&quot;sieben&quot;<br />\n'
                                      '</strong><br />'),
                         '{\\bf "`sieben"\'\\\\\n }')

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
                    r'{\bf Mitglieder}\\',
                    r'Name1\\',
                    r'Name2')))

        self.assertEqual(self.convert('<p><strong><br />Text</strong></p>'),
                         r'{\bf Text}')

    def test_curly_bracket_spaces(self):
        # If there is no space at left of the curly brackets, there will
        # not be any space in the displayed text (PDF), but in HTML it
        # is (with the bold-tag in HTML the browser displays a bold space).

        self.assertEqual(self.convert('text<b> bold text</b>'),
                         'text {\\bf bold text}')

        self.assertEqual(self.convert('text<strong> bold text</strong>'),
                         'text {\\bf bold text}')

        self.assertEqual(self.convert('te<b>X</b>t'),
                         'te{\\bf X}t')

        self.assertEqual(self.convert('a<em> b</em> c'),
                         'a {\\em b} c')

        self.assertEqual(self.convert('a<u> b</u> c'),
                         'a {\\em b} c')

        self.assertEqual(self.convert('a<i> b</i> c'),
                         'a {\\it b} c')

        self.assertEqual(self.convert('a <i>b</i> c'),
                         'a {\\it b} c')

        self.assertEqual(self.convert('a<i>b</i>c'),
                         'a{\\it b}\\/c')

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
            'Hello {\\bf my} world')

        self.assertEqual(
            self.convert('<span style="font-weight: bold;">test</span>'),
            '{\\bf test}')

        self.assertEqual(
            self.convert('<span style="font-weight: bold">test</span>'),
            '{\\bf test}')

    def test_sepcial_characters(self):
        self.assertEqual(self.convert('!#$%&amp;\'()*+-./02345'),
                         "!\\#$\\%\\&'()*+-./02345")

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
            self.convert('&laquo;&not;&reg;&macr;&deg;'
                         '&plusmn;&sup2;&sup3;&acute;&micro;'),
            '«¬®¯°±²³´µ')

        self.assertEqual(
            self.convert('&para;&middot;&cedil;&sup1;&ordm;'
                         '&raquo;&frac14;&frac12;&frac34;&iquest;'),
            '¶·¸¹º»¼½¾¿')

        self.assertEqual(
            self.convert('ÀÁÂÃÅÆÇÈÉ'),
            'ÀÁÂÃÅÆÇÈÉ')

        self.assertEqual(
            self.convert('ÊËÌÍÎÏÐÑÒÓ'),
            'ÊËÌÍÎÏÐÑÒÓ')

        self.assertEqual(
            self.convert('ÔÕÖ&times;ØÙÚÛÜÝ'),
            'ÔÕÖ×ØÙÚÛÜÝ')

        self.assertEqual(
            self.convert('Þßàáâãäåæç'),
            'Þßàáâãäåæç')

        self.assertEqual(
            self.convert('èéêëìíîïðñ'),
            'èéêëìíîïðñ')

        self.assertEqual(
            self.convert('òóôõö&divide;øùúû'),
            'òóôõö÷øùúû')

        self.assertEqual(
            self.convert('üüýþÿŒœ&sbquo;&bdquo;'),
            'üüýþÿŒœ‚„')

        self.assertEqual(
            self.convert('&hellip;&trade;&bull;&rarr;&rArr;&hArr;&asymp;'),
            '…™•→⇒⇔≈')

        # unsupported sepcial chars:
        self.assertEqual(
            self.convert('&yen;&brvbar;‛&diams;►'),
            '')

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
                         r'C:\\Programs\\foo')

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
        latex = (r'{\bf foo} ' * times).strip()

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

    def test_space_after_italic(self):
        html = 'foo <em>bar</em> baz'
        latex = r'foo {\em bar} baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <u>bar</u> baz'
        latex = r'foo {\em bar} baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <i>bar</i> baz'
        latex = r'foo {\it bar} baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo (<em>bar</em>) baz'
        latex = r'foo ({\em bar}\/) baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo (<u>bar</u>) baz'
        latex = r'foo ({\em bar}\/) baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo (<i>bar</i>) baz'
        latex = r'foo ({\it bar}\/) baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <em>bar</em>-baz'
        latex = r'foo {\em bar}\/-baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <u>bar</u>-baz'
        latex = r'foo {\em bar}\/-baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <i>bar</i>-baz'
        latex = r'foo {\it bar}\/-baz'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <em>bar</em>'
        latex = r'foo {\em bar}'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <u>bar</u>'
        latex = r'foo {\em bar}'
        self.assertEqual(self.convert(html), latex)

        html = 'foo <i>bar</i>'
        latex = r'foo {\it bar}'
        self.assertEqual(self.convert(html), latex)

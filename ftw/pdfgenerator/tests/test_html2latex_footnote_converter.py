# pylint: disable=W0212, W0201
# W0212: Access to a protected member of a client class
# W0201: Attribute defined outside __init__

from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.testing import MockTestCase


LATEX_FOOTNOTE = r'%(text)s\footnote{%(footnote)s}'


class TestFootnoteConverter(MockTestCase):

    def setUp(self):
        super(TestFootnoteConverter, self).setUp()

        self.context = self.mocker.mock(count=False)
        self.expect(self.context.absolute_url()).result(
            'http://nohost/plone')

        self.layout = self.mocker.mock()

        self.converter = HTML2LatexConverter(
            context=self.context,
            request=object(),
            layout=self.layout)

        self.convert = self.converter.convert

    def test_basic_fn_syntax(self):
        self.replay()
        html = ('<span class="footnote" data-footnote="thefn">'
                'complicated</span>')
        latex = LATEX_FOOTNOTE % {'text': 'complicated',
                                  'footnote': 'thefn'}
        self.assertEqual(self.convert(html), latex)

    def test_fn_with_icon(self):
        self.replay()
        html = ('<span class="footnote" data-footnote="thefn">complicated'
                '<i class="some-icon"></i></span>')
        latex = LATEX_FOOTNOTE % {'text': r'complicated\textit{}',
                                  'footnote': 'thefn'}
        self.assertEqual(self.convert(html), latex)

    def test_fn_with_custom_classes(self):
        self.replay()
        html = ('<span class="classa footnote classb" '
                'data-footnote="thefn">complicated</span>')
        latex = LATEX_FOOTNOTE % {'text': r'complicated',
                                  'footnote': 'thefn'}
        self.assertEqual(self.convert(html), latex)

    def test_fn_with_custom_attributes(self):
        self.replay()
        html = ('<span stuff="ignored" class="footnote" '
                'id="nonrelevant" data-footnote="thefn">complicated</span>')
        latex = LATEX_FOOTNOTE % {'text': r'complicated',
                                  'footnote': 'thefn'}
        self.assertEqual(self.convert(html), latex)

    def test_footnote_without_data_footnote_attribute_is_ignored(self):
        self.replay()
        html = ('<span class="footnote">complicated</span>')
        self.assertEqual(self.convert(html), 'complicated')

    def test_span_without_footnote_is_ignored(self):
        self.replay()
        html = ('<span>complicated</span>')
        self.assertEqual(self.convert(html), 'complicated')

    def test_footnote_with_newlines(self):
        self.replay()
        html = ('<span class="footnote" data-footnote="fn\ntext">'
                'complicated</span>')
        latex = LATEX_FOOTNOTE % {'text': 'complicated',
                                  'footnote': 'fn text'}
        self.assertEqual(self.convert(html), latex)

    def test_footnote_with_umlauts(self):
        self.replay()
        html = (u'<span class="footnote" data-footnote="\xfcbl\xe4">'
                u'c\xf6mpli\xe7ated</span>')
        latex = LATEX_FOOTNOTE % {'text': 'c\xc3\xb6mpli\xc3\xa7ated',
                                  'footnote': '\xc3\xbcbl\xc3\xa4'}
        self.assertEqual(self.convert(html), latex)

# pylint: disable=W0212, W0201
# W0212: Access to a protected member of a client class
# W0201: Attribute defined outside __init__

from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.testing import MockTestCase


LATEX_HREF = r'\href{%(url)s}{%(label)s\footnote{\href{%(url)s}' + \
    r'{\url{%(url_label)s}}}}'


class TestHyperlinkConverter(MockTestCase):

    def setUp(self):
        super(TestHyperlinkConverter, self).setUp()

        self.context = self.mocker.mock(count=False)
        self.expect(self.context.absolute_url()).result(
            'http://nohost/plone')

        self.layout = self.mocker.mock()
        self.expect(self.layout.use_package('url', 'hyphens')).count(1, None)
        self.expect(self.layout.use_package('hyperref')).count(1, None)

        self.converter = HTML2LatexConverter(
            context=self.context,
            request=object(),
            layout=self.layout)

        self.convert = self.converter.convert

        self.reference_catalog = self.mocker.mock(count=False)
        self.mock_tool(self.reference_catalog, 'reference_catalog')

    def test_converts_urls(self):
        self.replay()
        html = '<a href="http://www.google.com/">guugel</a>'
        latex = LATEX_HREF % {'label': 'guugel',
                              'url': 'http://www.google.com/',
                              'url_label': 'http://www.google.com/'}
        self.assertEqual(self.convert(html), latex)

    def test_relative_urls(self):
        self.replay()
        html = '<a href="./foo/bar">baz</a>'
        latex = LATEX_HREF % {
            'label': 'baz',
            'url': 'http://nohost/plone/foo/bar',
            'url_label': 'http://nohost/plone/foo/bar'}
        self.assertEqual(self.convert(html), latex)

        html = '<a href="foo/bar">baz</a>'
        latex = LATEX_HREF % {
            'label': 'baz',
            'url': 'http://nohost/plone/foo/bar',
            'url_label': 'http://nohost/plone/foo/bar'}
        self.assertEqual(self.convert(html), latex)

    def test_links_within_brackets(self):
        self.replay()
        html = 'foo (<a href="http://google.com">bar</a>) baz'
        latex = r'foo (%s) baz' % LATEX_HREF % {
            'label': 'bar',
            'url': 'http://google.com',
            'url_label': 'http://google.com'}
        self.assertEqual(self.convert(html), latex)

    def test_hyphens_in_links(self):
        self.replay()
        html = '<a href="http://my-page.com">foo</a>'
        latex = LATEX_HREF % {'label': 'foo',
                              'url': 'http://my-page.com',
                              'url_label': 'http://my-page.com'}
        self.assertEqual(self.convert(html), latex)

    def test_mailto_links(self):
        self.replay()
        html = '<a href="mailto:info@google.com">foo</a>'
        latex = LATEX_HREF % {'label': 'foo',
                              'url': 'mailto:info@google.com',
                              'url_label': 'info@google.com'}
        self.assertEqual(self.convert(html), latex)

    def test_spaces_in_links(self):
        self.replay()
        html = '<a href="http://foo/foo%20bar%20baz">foo</a>'
        latex = LATEX_HREF % {
            'label': 'foo',
            'url': 'http://foo/foo\%20bar\%20baz',
            'url_label': 'http://foo/foo\%20bar\%20baz'}
        self.assertEqual(self.convert(html), latex)

        html = '<a href="mailto:info@google.com?subject=foo%20bar%20baz">' +\
            'foo</a>'
        latex = LATEX_HREF % {
            'label': 'foo',
            'url': 'mailto:info@google.com?subject=foo\%20bar\%20baz',
            'url_label': 'info@google.com?subject=foo\%20bar\%20baz'}
        self.assertEqual(self.convert(html), latex)

        html = '<a href="mailto:info@google.com?subject=foo bar baz">foo</a>'
        latex = LATEX_HREF % {
            'label': 'foo',
            'url': 'mailto:info@google.com?subject=foo\%20bar\%20baz',
            'url_label': 'info@google.com?subject=foo\%20bar\%20baz'}
        self.assertEqual(self.convert(html), latex)

    def test_ampersand_in_links(self):
        self.replay()
        html = '<a href="http://host.com/?foo=1&amp;bar=2">baz</a>'
        latex = LATEX_HREF % {'label': 'baz',
                              'url': 'http://host.com/?foo=1\\&bar=2',
                              'url_label': 'http://host.com/?foo=1\\&bar=2'}
        self.assertEqual(self.convert(html), latex)

        html = '<a href="http://host.com/?foo=1&bar=2">baz</a>'
        latex = LATEX_HREF % {'label': 'baz',
                              'url': 'http://host.com/?foo=1\\&bar=2',
                              'url_label': 'http://host.com/?foo=1\\&bar=2'}
        self.assertEqual(self.convert(html), latex)

    def test_underscores_in_links(self):
        self.replay()
        html = '<a href="http://host.com/foo_bar">baz</a>'
        latex = LATEX_HREF % {'label': 'baz',
                              'url': 'http://host.com/foo_bar',
                              'url_label': 'http://host.com/foo\_bar'}
        self.assertEqual(self.convert(html), latex)

    def test_underscores_in_links2(self):
        self.replay()
        html = '<a href="http://test.com/_something#anchor">http://test.com/_something#anchor</a>'
        latex = r'\href{http://test.com/_something\#anchor}{http://test.com/\_something\#anchor\footnote{\href{http://test.com/_something\#anchor}{\url{http://test.com/\_something\#anchor}}}}'
        self.assertMultiLineEqual(latex + '\n',
                                  self.convert(html) + '\n')

    def test_hash_key_in_links(self):
        self.replay()
        html = '<a href="http://host.com/foo#bar">baz</a>'
        latex = LATEX_HREF % {'label': 'baz',
                              'url': 'http://host.com/foo\\#bar',
                              'url_label': 'http://host.com/foo\\#bar'}
        self.assertEqual(self.convert(html), latex)

    def test_additional_parameters(self):
        self.replay()
        html = 'foo <a color="red" href="http://nohost/bar" class="link">' + \
            'bar</a> baz'
        latex = r'foo %s baz' % LATEX_HREF % {
            'label': 'bar',
            'url': 'http://nohost/bar',
            'url_label': 'http://nohost/bar'}

        self.assertEqual(self.convert(html), latex)

    def test_multiple_links(self):
        self.replay()
        html = '<a href="http://foo">foo</a> <a href="http://bar">bar</a> ' +\
            '<a href="http://baz">baz</a>'

        link1 = LATEX_HREF % {'label': 'foo',
                              'url': 'http://foo',
                              'url_label': 'http://foo'}

        link2 = LATEX_HREF % {'label': 'bar',
                              'url': 'http://bar',
                              'url_label': 'http://bar'}

        link3 = LATEX_HREF % {'label': 'baz',
                              'url': 'http://baz',
                              'url_label': 'http://baz'}

        latex = ' '.join((link1, link2, link3))

        self.assertEqual(self.convert(html), latex)

    def test_other_protocols(self):
        self.replay()
        protocols = ['http', 'https', 'ftp', 'file']

        for protocol in protocols:
            html = '<a href="%s://foo/bar">baz</a>' % protocol
            latex = LATEX_HREF % {'label': 'baz',
                                  'url': '%s://foo/bar' % protocol,
                                  'url_label': '%s://foo/bar' % protocol}
            self.assertEqual(self.convert(html), latex)

    def test_label_is_converted(self):
        self.replay()
        html = '<a href="http://foo">foo <b>bar</b> baz</a>'
        latex = LATEX_HREF % {'label': r'foo \textbf{bar} baz',
                              'url': 'http://foo',
                              'url_label': 'http://foo'}
        self.assertEqual(self.convert(html), latex)

    def test_no_escaped_dashes_in_label(self):
        # In a \href{} environment, a-b should not become a"=b because
        # this will be printend literal.
        self.replay()
        html = '<a href="http://foo">x-y</a>'
        latex = LATEX_HREF % {'label': r'x-y',
                              'url': 'http://foo',
                              'url_label': 'http://foo'}
        self.assertEqual(self.convert(html), latex)

    def test_removes_nonbreaking_spaces(self):
        self.replay()
        # Non break spaces are evil. In HTML they are usually not used the
        # way they should be used in LaTeX, so we replace them with spaces.
        html = u'<a href="http://host">Hello\xa0World</a>'.encode('utf8')
        latex = LATEX_HREF % {'label': 'Hello World',
                              'url': 'http://host',
                              'url_label': 'http://host'}
        self.assertEqual(self.convert(html), latex)

    def test_resolveuid_links_are_resolved(self):
        obj = self.context.stub()
        self.expect(obj.absolute_url()).result('http://nohost/theobj')

        self.expect(self.reference_catalog.lookupObject('THEUID')).result(obj)
        self.replay()

        html = '<a href="./resolveuid/THEUID">The Obj</a>'
        latex = LATEX_HREF % {'label': 'The Obj',
                              'url': 'http://nohost/theobj',
                              'url_label': 'http://nohost/theobj'}
        self.assertEqual(self.convert(html), latex)

        html = '<a href="./resolveUid/THEUID">The Obj</a>'
        latex = LATEX_HREF % {'label': 'The Obj',
                              'url': 'http://nohost/theobj',
                              'url_label': 'http://nohost/theobj'}
        self.assertEqual(self.convert(html), latex)

    def test_links_in_listing_items(self):
        self.replay()

        # There should not be a non-escaped ampersand (&) within listing
        # items - even when in a href.
        html = '<ol><li><a href="%s">foo bar</a></li></ol>' % (
            'http://host/view?foo=1&bar=2')

        latex_link = LATEX_HREF % {
            'label': 'foo bar',
            'url': 'http://host/view?foo=1\\&bar=2',
            'url_label': 'http://host/view?foo=1\\&bar=2'}

        latex = '\n'.join((
                r'\begin{enumerate}',
                r'\item %s' % latex_link,
                r'\end{enumerate}',
                ))

        self.assertEqual(self.convert(html).strip(), latex)

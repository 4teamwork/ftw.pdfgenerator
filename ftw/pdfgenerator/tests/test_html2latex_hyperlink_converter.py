from Products import CMFCore
from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from mocker import ANY
from plone.mocktestcase import MockTestCase


class TestHyperlinkConverter(MockTestCase):

    def setUp(self):
        MockTestCase.setUp(self)

        self.context = self.mocker.mock(count=False)
        self.expect(self.context.absolute_url()).result(
            'http://nohost/plone')

        self.layout = self.mocker.mock()
        self.expect(self.layout.use_package('hyperref')).count(1, None)

        self.converter = HTML2LatexConverter(
            context=self.context,
            request=object(),
            layout=self.layout)

        self.convert = self.converter.convert

    def tearDown(self):
        if self._getToolByName_mock is not None:
            CMFCore.utils.getToolByName = self._ori_getToolByName
            self._getToolByName_mock = None

    def mock_tool(self, mock, name):
        """Register a mock tool that will be returned when getToolByName()
        is called.
        """

        if self._getToolByName_mock is None:
            self._ori_getToolByName = CMFCore.utils.getToolByName
            self._getToolByName_mock = self.mocker.replace(
                'Products.CMFCore.utils.getToolByName')
        self.expect(self._getToolByName_mock(ANY, name)).result(mock).count(
            0, None)

    def test_converts_urls(self):
        self.replay()
        html = '<a href="http://www.google.com/">guugel</a>'
        latex = r'\href{http://www.google.com/}{guugel}'
        self.assertEqual(self.convert(html), latex)

    def test_relative_urls(self):
        self.replay()
        html = '<a href="./foo/bar">baz</a>'
        latex = r'\href{http://nohost/plone/./foo/bar}{baz}'
        self.assertEqual(self.convert(html), latex)

        html = '<a href="foo/bar">baz</a>'
        latex = r'\href{http://nohost/plone/foo/bar}{baz}'
        self.assertEqual(self.convert(html), latex)

    def test_links_within_brackets(self):
        self.replay()
        html = 'foo (<a href="http://google.com">bar</a>) baz'
        latex = r'foo (\href{http://google.com}{bar}) baz'
        self.assertEqual(self.convert(html), latex)

    def test_hyphens_in_links(self):
        self.replay()
        html = '<a href="http://my-page.com">foo</a>'
        latex = r'\href{http://my-page.com}{foo}'
        self.assertEqual(self.convert(html), latex)

    def test_mailto_links(self):
        self.replay()
        html = '<a href="mailto:info@google.com">foo</a>'
        latex = r'\href{mailto:info@google.com}{foo}'
        self.assertEqual(self.convert(html), latex)

    def test_spaces_in_links(self):
        self.replay()
        html = '<a href="http://foo/foo%20bar%20baz">foo</a>'
        latex = r'\href{http://foo/foo\%20bar\%20baz}{foo}'
        self.assertEqual(self.convert(html), latex)

        html = '<a href="mailto:info@google.com?subject=foo%20bar%20baz">' +\
            'foo</a>'
        latex = r'\href{mailto:info@google.com?subject=foo\%20bar\%20baz}' +\
            r'{foo}'
        self.assertEqual(self.convert(html), latex)

        html = '<a href="mailto:info@google.com?subject=foo bar baz">foo</a>'
        latex = r'\href{mailto:info@google.com?subject=foo\%20bar\%20baz}' +\
            r'{foo}'
        self.assertEqual(self.convert(html), latex)

    def test_ampersand_in_links(self):
        self.replay()
        html = '<a href="http://host.com/?foo=1&amp;bar=2">baz</a>'
        latex = r'\href{http://host.com/?foo=1&bar=2}{baz}'
        self.assertEqual(self.convert(html), latex)

        html = '<a href="http://host.com/?foo=1&bar=2">baz</a>'
        latex = r'\href{http://host.com/?foo=1&bar=2}{baz}'
        self.assertEqual(self.convert(html), latex)

    def test_additional_parameters(self):
        self.replay()
        html = 'foo <a color="red" href="http://nohost/bar" class="link">' + \
            'bar</a> baz'
        latex = r'foo \href{http://nohost/bar}{bar} baz'

        self.assertEqual(self.convert(html), latex)

    def test_multiple_links(self):
        self.replay()
        html = '<a href="http://foo">foo</a> <a href="http://bar">bar</a> ' +\
            '<a href="http://baz">baz</a>'
        latex = r'\href{http://foo}{foo} \href{http://bar}{bar} ' + \
            r'\href{http://baz}{baz}'

        self.assertEqual(self.convert(html), latex)

    def test_other_protocols(self):
        self.replay()
        protocols = ['http', 'https', 'ftp', 'file']

        for protocol in protocols:
            html = '<a href="%s://foo/bar">baz</a>' % protocol
            latex = r'\href{%s://foo/bar}{baz}' % protocol
            self.assertEqual(self.convert(html), latex)

    def test_label_is_converted(self):
        self.replay()
        html ='<a href="http://foo">foo <b>bar</b> baz</a>'
        latex = r'\href{http://foo}{foo {\bf bar} baz}'
        self.assertEqual(self.convert(html), latex)

    def test_removes_nonbreaking_spaces(self):
        self.replay()
        # Non break spaces are evil. In HTML they are usually not used the
        # way they should be used in LaTeX, so we replace them with spaces.
        html = u'<a href="http://host">Hello\xa0World</a>'.encode('utf8')
        latex = r'\href{http://host}{Hello World}'
        self.assertEqual(self.convert(html), latex)

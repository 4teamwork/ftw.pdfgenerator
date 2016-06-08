# pylint: disable=W0212, W0201
# W0212: Access to a protected member of a client class
# W0201: Attribute defined outside __init__

from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.testing import MockTestCase


class TestURLConverter(MockTestCase):

    def setUp(self):
        super(TestURLConverter, self).setUp()

        self.context = self.mocker.mock(count=False)
        self.expect(self.context.absolute_url()).result(
            'http://nohost/plone')

        self.layout = self.mocker.mock()

        self.converter = HTML2LatexConverter(
            context=self.context,
            request=object(),
            layout=self.layout)

        self.convert = self.converter.convert

    def test_simple_url(self):
        self.replay()
        html = 'x http://domain.ch/foo/bar y'
        latex = 'x http://domain.ch""/foo""/bar y'
        self.assertEqual(self.convert(html), latex)

    def test_https_url(self):
        self.replay()
        html = 'x https://domain.ch/foo/bar y'
        latex = 'x https://domain.ch""/foo""/bar y'
        self.assertEqual(self.convert(html), latex)

    def test_advanced_url(self):
        self.replay()
        html = 'x http://usr@pwd:sub.domain.com/path/to/doc.html' + \
               '?foo=1&bar=2#anchor y'
        latex = 'x http://usr@pwd:sub.domain.com""/path""/to""/doc.html' + \
                '?foo=1&bar=2\\#anchor y'
        self.assertEqual(self.convert(html), latex)

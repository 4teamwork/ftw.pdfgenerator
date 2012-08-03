from ftw.pdfgenerator.html2latex.subconverters import htmlentities
from ftw.pdfgenerator.tests.base import SubconverterTestBase



class TestHtmlentitiesConverter(SubconverterTestBase):

    def test_converter_is_default(self):
        self.assertIn(
            htmlentities.HtmlentitiesConverter,
            self.converter.get_default_subconverters())

    def test_converter_converts_umlauts(self):
        self.assertEqual(self.convert('&auml;&euml;&iuml;&ouml;&uuml;'),
                         '\xc3\xa4\xc3\xab\xc3\xaf\xc3\xb6\xc3\xbc')
        self.assertEqual(self.convert('5 &lt; 6'),
                         '5 < 6')
        self.assertEqual(self.convert('Hello&nbsp;World'),
                         'Hello World')

    def test_converter_converts_xmlentities(self):
        # "&" should also be escaped by a later pattern.
        self.assertEqual(self.convert('m&#38;m'),
                         r'm\&m')

from ftw.pdfgenerator import babel
from ftw.testing import MockTestCase


class TestBabel(MockTestCase):

    def test_lookup_babel_option(self):
        self.assertEqual(babel.lookup_babel_option('en'), 'english')
        self.assertEqual(babel.lookup_babel_option('en-gb'), 'british')
        self.assertEqual(babel.lookup_babel_option('en-us'), 'USenglish')
        self.assertEqual(babel.lookup_babel_option('en-gm'), 'english')

    def test_get_preferred_babel_option_for_context(self):
        foo = self.mocker.mock()
        self.expect(foo.getLanguage).result(lambda: 'de-at')

        language_tool = self.mocker.mock()
        self.mock_tool(language_tool, 'portal_languages')
        self.expect(language_tool.getPreferredLanguage()).result('de')

        bar = self.mocker.mock()
        self.expect(getattr(bar, 'getLanguage', None)).result(None)

        self.replay()

        self.assertEqual(babel.get_preferred_babel_option_for_context(foo),
                         'naustrian')
        self.assertEqual(babel.get_preferred_babel_option_for_context(bar),
                         'ngerman')

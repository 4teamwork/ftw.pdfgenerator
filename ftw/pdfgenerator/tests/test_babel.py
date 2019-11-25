from ftw.pdfgenerator import babel
from ftw.testing import MockTestCase


class TestBabel(MockTestCase):

    def test_lookup_babel_option(self):
        self.assertEqual(babel.lookup_babel_option('en'), 'english')
        self.assertEqual(babel.lookup_babel_option('en-gb'), 'british')
        self.assertEqual(babel.lookup_babel_option('en-us'), 'USenglish')
        self.assertEqual(babel.lookup_babel_option('en-gm'), 'english')

    def test_get_preferred_babel_option_for_context(self):
        foo = self.mock()
        foo.getLanguage.return_value = 'de-at'

        language_tool = self.mock()
        self.mock_tool(language_tool, 'portal_languages')
        language_tool.getPreferredLanguage.return_value = 'de'

        bar = self.mock()
        bar.getLanguage = None

        self.assertEqual(babel.get_preferred_babel_option_for_context(foo),
                         'naustrian')
        self.assertEqual(babel.get_preferred_babel_option_for_context(bar),
                         'ngerman')

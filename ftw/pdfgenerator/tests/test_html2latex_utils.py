from ftw.pdfgenerator.html2latex.utils import generate_manual_caption
from ftw.pdfgenerator.testing import ZCML_WITH_SITE_LAYER
from ftw.testing import MockTestCase


class TestGenerateManualCaption(MockTestCase):

    layer = ZCML_WITH_SITE_LAYER

    def test_empty_caption(self):
        self.assertEqual(generate_manual_caption('', 'table'), '')
        self.assertEqual(generate_manual_caption(None, 'table'), '')

    def test_wrong_index(self):
        with self.assertRaises(ValueError) as cm:
            generate_manual_caption('foo', 'wrong')

        self.assertEqual(
            str(cm.exception),
            'Environment must be one of "table", "figure". Got "wrong".')

    def test_table_caption(self):
        latex = generate_manual_caption('The Caption', 'table')
        self.assertIn(r'\addtocounter{table}{1}', latex)
        self.assertIn(r'\addcontentsline{lot}{table}', latex)
        self.assertIn(r'\ignorespaces The Caption', latex)
        self.assertIn(r'Table \thechapter.\arabic{table}: The Caption',
                      latex)

    def test_figure_caption(self):
        latex = generate_manual_caption('The Caption', 'figure')
        self.assertIn(r'\addtocounter{figure}{1}', latex)
        self.assertIn(r'\addcontentsline{lof}{figure}', latex)
        self.assertIn(r'\ignorespaces The Caption', latex)
        self.assertIn(r'Figure \thechapter.\arabic{figure}: The Caption',
                      latex)

    def test_not_listed_table_caption(self):
        latex = generate_manual_caption('The Caption', 'table',
                                        show_in_index=False)

        self.assertNotIn(r'\addtocounter{table}{1}', latex)
        self.assertNotIn(r'\addcontentsline{lot}{table}', latex)
        self.assertNotIn(r'\ignorespaces The Caption', latex)
        self.assertNotIn(r'Table \thechapter.\arabic{table}: The Caption',
                      latex)
        self.assertIn(r'The Caption',
                      latex)

    def test_caption_with_umlaut(self):
        latex = generate_manual_caption('hall\xc3\xb6chen', 'table')
        self.assertIn(
            'Table \\thechapter.\\arabic{table}: hall\xc3\xb6chen',
            latex)

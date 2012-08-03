from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from unittest2 import TestCase


class SubconverterTestBase(TestCase):

    def setUp(self):
        TestCase.setUp(self)

        self.converter = HTML2LatexConverter(
            context=object(),
            request=object(),
            layout=object())

        self.convert = self.converter.convert

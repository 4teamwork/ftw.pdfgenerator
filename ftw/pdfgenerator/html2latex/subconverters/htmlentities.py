from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.html2latex import subconverter
from ftw.pdfgenerator.utils import decode_htmlentities


class HtmlentitiesConverter(subconverter.SubConverter):

    pattern = r'\\&(\w*);'
    placeholder = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM

    def __call__(self):
        html = self.get_html()[1:]
        latex = decode_htmlentities(html).encode('utf8')
        self.replace(latex)

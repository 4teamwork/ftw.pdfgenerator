from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.html2latex import subconverter
from ftw.pdfgenerator.utils import decode_htmlentities


class HtmlentitiesConverter(subconverter.SubConverter):

    # e.g. Matches named "&auml;", numeric "&#13;" and hexadecimal "&#xE4;" entities
    pattern = r'\\?&\\?(#?)(\d{1,5}|\w{1,8}|x[\w\d]{1,5});'
    placeholder = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM

    def __call__(self):
        html = self.get_html()
        latex = decode_htmlentities(html).encode('utf8')
        self.replace(latex)

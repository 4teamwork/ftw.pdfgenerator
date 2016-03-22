from ftw.pdfgenerator.html2latex import subconverter
import re


class FootnoteConverter(subconverter.SubConverter):

    pattern = (r'<span [^>]*?class="(?P<class>[^"]*?footnote[^"]*?)"[^>]*?>'
               '(?P<content>.*?)</span>')

    def __call__(self):
        if 'footnote' not in self.match.group('class').split():
            return

        fntext_match = re.search(r'data-footnote="(?P<footnoteText>[^"]*)"', self.get_html())
        if not fntext_match:
            return
        footnoteText = fntext_match.group('footnoteText')

        content = self.match.group('content')

        content = self.converter.convert(content)
        footnoteText = self.converter.convert(footnoteText)
        latex = r'%s\footnote{%s}' % (content, footnoteText)

        self.replace_and_lock(latex)

from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.html2latex import subconverter
import re

def find_bracket_range(latex):
    opening = -1
    brackets = 0
    xpr = re.compile('[\{\}]')

    for match in xpr.finditer(latex):
        if match.group() == '{':
            if opening == -1:
                opening = match.span()[0]
            brackets += 1

        elif match.group() == '}':
            if opening != -1:
                brackets -= 1

        if opening != -1 and brackets == 0:
            return opening, match.span()[1]

    return None


class Textformatting(subconverter.SubConverter):
    """ This converter fixes newlines within text formatting commands:

    "\textbf{*\n\n*}" is not allowed, use "\textbf{*\\*}"
    "\textit{*\n\n*}" is not allowed, use "\textit{*\\*}"
    "\emph{*\n\n*}" is not allowed, use "\emph{*\\*}"

    It also not allowed to have multiple newlines (\\{1,}) in those
    environments.
    Since we sometimes we have this situation and we cannot end the
    paragraph we need to fix it with \vspace's.
    """

    pattern = r'(\\(textbf|textit|emph){.*})'
    placeholder = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER_BOTTOM

    def __call__(self):
        latex = self.get_html()
        head, tail = find_bracket_range(latex)

        before = latex[:head]
        environment = latex[head:tail]
        after = latex[tail:]

        environment = self.convert_substring(environment)

        latex = before + environment + after
        self.replace(latex)

    def convert_substring(self, latex):
        latex = latex.replace(r'\\', '\n')

        latex = re.sub(r'([^\n])\n', r'\g<1>\\\\', latex)
        latex = re.sub(r'\n+', r'\\vspace{\\baselineskip}', latex)

        return latex

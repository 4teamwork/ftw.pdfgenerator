from ftw.pdfgenerator import interfaces
from zope.interface import implements


class SubConverter(object):
    implements(interfaces.ISubConverter)

    # regular expression
    pattern = None
    placeholder = interfaces.HTML2LATEX_CUSTOM_PATTERN_PLACEHOLDER

    def __init__(self, converter, match, html):
        self.converter = converter
        self.match = match
        self.fullhtml = html

    def __call__(self):
        """This method should be implemented when subclassing.
        """
        raise NotImplementedError()

    def get_html(self):
        return self.fullhtml[self.match.start():self.match.end()]

    def replace_and_lock(self, latex):
        return self.converter.replace_and_lock(
            self.match.start(),
            self.match.end(),
            latex)

    def replace(self, latex):
        return self.converter.replace(
            self.match.start(),
            self.match.end(),
            latex)

    def get_context(self):
        return self.converter.converter.context

    def get_layout(self):
        return self.converter.converter.layout

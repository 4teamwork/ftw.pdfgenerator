from ftw.pdfgenerator.html2latex import subconverter
from urlparse import urlparse
from urlparse import urlunparse


class URLConverter(subconverter.SubConverter):
    """Converts URLs within text (not link tags) so that they
    support hyphenation.
    """

    # http://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    def __call__(self):
        url = self.get_html()
        scheme, netloc, path, params, query, fragment = urlparse(url)
        path = path.replace('/', '""/')
        url = urlunparse((scheme, netloc, path, params, query, fragment))
        url = url.replace('/""/', '""/', 1)
        self.replace_and_lock(url)

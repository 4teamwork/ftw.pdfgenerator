from ftw.pdfgenerator.html2latex import subconverter
from urlparse import urlparse
from urlparse import urlunparse


class URLConverter(subconverter.SubConverter):
    """Convert URLs within text (not link tags).

    * Add hyphenation hints onto path segments
    * Add hyphenation hints onto query string parametres
    * Convert xml entities from minidom `element.toxml()`
    * Escape latex nasties for link tags
    """

    # http://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    def __call__(self):
        url = self.get_html()
        scheme, netloc, path, params, query, fragment = urlparse(url)

        # Make path segments hyphenable
        path = '""/'.join(path.split('/'))

        # Handle minidom `element.toxml()`
        query = query.replace('&amp;', '&')

        # Make query string parametres hyphenable
        query = query.replace('&', '""&')

        url = urlunparse((scheme, netloc, path, params, query, fragment))

        # Work around urlunparse() treating the hyphenation hint as a segment
        url = url.replace('/""/', '""/', 1)

        # Replace latex nasties for conversion
        url = url.replace('_', r'\_')
        url = url.replace('&', r'\&')
        url = url.replace('#', r'\#')
        url = url.replace('%', r'\%')

        self.replace_and_lock(url)

from BeautifulSoup import BeautifulSoup
from ftw.pdfgenerator.html2latex import subconverter
from ftw.pdfgenerator.utils import html2xmlentities
from xml.dom import minidom


class ListConverter(subconverter.SubConverter):
    """
    The ListConverter converts <ul> and <ol> lists
    into latex' itemize- and enumerate-environments.
    """

    pattern = r'<(ul|ol)(.*)</\1>'
    listing_tag_mapping = {
        'ul' : 'itemize',
        'ol' : 'enumerate',
    }

    def __call__(self):
        html = self.get_html()
        # cleanup html with BeautifulSoup
        html = str(BeautifulSoup(html))

        # minidom hates htmlentities, but loves xmlentities -.-
        html = '<dummy>%s</dummy>' % html
        html = html2xmlentities(html)

        # parse DOM
        dom = minidom.parseString(html)
        latex = []

        for node in dom.getElementsByTagName('dummy')[0].childNodes:
            if node.nodeType == 1 and \
                    node.tagName.lower() in self.listing_tag_mapping.keys():

                # iterate, because there may be multiple lists
                begin_env, end_env = self._create_environ(node)

                latex.append(begin_env)
                for elm in node.childNodes:

                    if elm.nodeType==3:
                        content_html = elm.toxml().strip()

                    else:
                        content_html = ''.join(
                            [e.toxml() for e in elm.childNodes])

                    if elm.nodeType == 1 and elm.tagName.lower() == 'li':
                        latex.append(
                            (r'\item %s' %
                             self.converter.convert(content_html)).strip())

                    else:
                        data = self.converter.convert(content_html).strip()
                        if len(data) > 0:
                            latex.append(data)

                latex.append(end_env)

            else:
                latex.append(self.converter.convert(node.toxml()))

        latex.append('')
        self.replace_and_lock('\n'.join(latex))

    def _create_environ(self, list_):
        name = list_.tagName.lower()
        env = self.listing_tag_mapping[name]

        return (r'\begin{%s}' % env,
                r'\end{%s}' % env)

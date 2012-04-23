from BeautifulSoup import BeautifulSoup
from ftw.pdfgenerator.html2latex import subconverter
from ftw.pdfgenerator.utils import html2xmlentities
from xml.dom import minidom


class ListConverter(subconverter.SubConverter):
    """
    The ListConverter converts <ul> and <ol> lists
    into latex' itemize- and enumerate-environments.
    """

    pattern = r'<(ul|ol|dl)(.*)</\1>'
    listing_tag_mapping = {
        'ul': 'itemize',
        'ol': 'enumerate',
        'dl': 'description',
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
            if node.nodeType == minidom.Node.ELEMENT_NODE and \
                    node.tagName.lower() in self.listing_tag_mapping.keys():

                latex.extend(self._convert_listing_environment(node))

            else:
                latex.append(self.converter.convert(node.toxml()))

        latex.append('')
        self.replace_and_lock('\n'.join(latex))

    def _convert_listing_environment(self, node):
        """Converts a <ul>, <ol> or <dl> node to latex.
        """
        latex = []

        if node.tagName.lower() in ('ol', 'ul'):
            nodes_latex = self._convert_listing_items(node)

        else:
            nodes_latex = self._convert_description_items(node)

        has_items = self._listing_has_items(node)
        if nodes_latex and has_items:
            begin_env, end_env = self._create_environ(node)

            latex.append(begin_env)
            latex.append(nodes_latex)
            latex.append(end_env)
            return latex

        elif nodes_latex:
            return [nodes_latex]

        else:
            return []

    def _listing_has_items(self, node):
        for elm in node.childNodes:
            if elm.nodeType == minidom.Node.ELEMENT_NODE and \
                    elm.tagName.lower() in ('li', 'dt', 'dd'):
                return True
        return False

    def _convert_listing_items(self, list_node):
        """Converts <li> nodes to LaTeX.
        """
        latex = []
        for elm in list_node.childNodes:
            if elm.nodeType == minidom.Node.ELEMENT_NODE and \
                    elm.tagName.lower() == 'li':
                latex.append(r'\item %s' % (
                        self._get_node_content(elm).strip()))

            elif elm.nodeType == minidom.Node.ELEMENT_NODE and \
                    elm.tagName.lower() in self.listing_tag_mapping.keys():
                latex.extend(self._convert_listing_environment(elm))

            else:
                content_latex = self._get_node_content(elm)
                if content_latex is not None:
                    latex.append(content_latex)

        return '\n'.join(latex)

    def _convert_description_items(self, list_node):
        """Converts <dt> / <dd> nodes to LaTeX.
        """
        latex = []

        dt_node = None
        for elm in list_node.childNodes:
            if elm.nodeType == minidom.Node.ELEMENT_NODE and \
                    elm.tagName.lower() == 'dt':
                dt_node = elm

            elif elm.nodeType == minidom.Node.ELEMENT_NODE and \
                    elm.tagName.lower() == 'dd' and \
                    dt_node is not None:
                latex.append(r'\item[%s] %s' % (
                        self._get_node_content(dt_node).strip(),
                        self._get_node_content(elm).strip()))
                dt_node = None

            elif elm.nodeType == minidom.Node.ELEMENT_NODE and \
                    elm.tagName.lower() in self.listing_tag_mapping.keys():
                latex.extend(self._convert_listing_environment(elm))

            else:
                content_latex = self._get_node_content(elm)
                if content_latex is not None:
                    latex.append(content_latex)

        return '\n'.join(latex)

    def _get_node_content(self, elm):
        """Returns the LaTeX for the node `elm`.
        """
        if elm.nodeType == minidom.Node.TEXT_NODE:
            content_html = elm.toxml().strip()

        else:  # tag node
            content_html = ''.join(
                [e.toxml() for e in elm.childNodes])

        if len(content_html) == 0:
            return None

        else:
            return self.converter.convert(content_html)

    def _create_environ(self, list_):
        """Creates an environment for the node `list_`.
        """
        name = list_.tagName.lower()
        env = self.listing_tag_mapping[name]

        return (r'\begin{%s}' % env,
                r'\end{%s}' % env)

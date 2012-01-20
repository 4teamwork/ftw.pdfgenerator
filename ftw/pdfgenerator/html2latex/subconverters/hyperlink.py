from ftw.pdfgenerator.html2latex import subconverter
import os.path


class HyperlinkConverter(subconverter.SubConverter):

    pattern = r'<a.*?href="(.*?)".*?>(.*?)</a>'

    def __call__(self):
        context = self.get_context()

        url, label = self.match.groups()
        label = self.converter.convert(label)

        is_relative = '://' not in url and not url.startswith('mailto:')

        if is_relative:
            url = os.path.join(context.absolute_url(), url)

        url = url.replace('&amp;', '&')
        url = url.replace(' ', '%20').replace('%', '\%')

        self.get_layout().use_package('hyperref')
        self.replace_and_lock(self.latex_link(url, label))

    def latex_link(self, url, label):
        return r'\href{%s}{%s}' % (url, label)

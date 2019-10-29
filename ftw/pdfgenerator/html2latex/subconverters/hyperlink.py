from Products.CMFCore.utils import getToolByName
from ftw.pdfgenerator.html2latex import subconverter
import os.path
import re


class HyperlinkConverter(subconverter.SubConverter):

    pattern = r'<a.*?href="(.*?)".*?>(.*?)</a>'

    def __call__(self):
        context = self.get_context()

        url, label = self.match.groups()
        label = (self.converter.convert(label)
                 .replace('""/', '/')
                 .replace('"=', '-'))

        is_relative = '://' not in url and not url.startswith('mailto:')

        if is_relative:
            url = os.path.join(context.absolute_url(), url)
            url = url.replace('/./', '/')

        url = self.resolve_uid(url)

        url = url.replace('&amp;', '&')
        url = url.replace('&', '\\&')
        url = url.replace(' ', '%20').replace('%', '\%')
        url = url.replace('#', '\#')

        # Do not display "mailto:"
        url_label = re.sub('^mailto:', '', url)
        url_label = url_label.replace('_', '\_')
        url_label = url_label.replace('""/', '/')

        self.get_layout().use_package('url', 'hyphens')
        self.get_layout().use_package('hyperref')
        self.replace_and_lock(self.latex_link(url, label, url_label))

    def latex_link(self, url, label, url_label):
        href = r'\href{%s}{%s}'
        footnote = r'\footnote{%s}' % href % (url, r'\url{%s}' % url_label)
        return href % (url, label + footnote)

    def resolve_uid(self, url):
        if '/' not in url:
            return url

        parts = url.split('/')
        if parts[-2] == 'resolveuid' or parts[-2] == 'resolveUid':
            context = self.converter.converter.context
            reference_catalog = getToolByName(context, 'reference_catalog')

            uid = parts[-1]
            obj = reference_catalog.lookupObject(uid)

            if obj is not None:
                url = obj.absolute_url()

        return url

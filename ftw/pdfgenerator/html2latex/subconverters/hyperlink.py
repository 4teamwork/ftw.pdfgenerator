from Products.CMFCore.utils import getToolByName
from ftw.pdfgenerator.html2latex import subconverter
import os.path
import re


class HyperlinkConverter(subconverter.SubConverter):

    pattern = r'<a.*?href="(.*?)".*?>(.*?)</a>'

    def __call__(self):
        context = self.get_context()

        portal_transforms = getToolByName(context, 'portal_transforms')
        html = portal_transforms.convert(
            'fck_ruid_to_url', self.get_html(), context=context)

        match = re.compile(self.pattern).search(html)
        url, label = match.groups()
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

from ftw.pdfgenerator.interfaces import DEBUG_MODE_COOKIE_KEY
from ftw.pdfgenerator.interfaces import IPDFAssembler
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class ExportPDFView(BrowserView):
    """Export a PDF with default settings. If the user is a Admin (if he
    has Manage portal permission), a additional form will be shown, where
    he can selected the desired output format (PDF, LaTeX only or ZIP).
    """

    index = ViewPageTemplateFile('export_pdf.pt')

    def __call__(self):
        if self.allow_alternate_output():
            if self.request.get('submitted', False):
                output = self.request.get('output')
                return self.export(output)

            return self.index()

        return self.export()

    def allow_alternate_output(self):
        """For selecting the output format, the user must have Manage portal
        permission.
        """
        user = self.context.portal_membership.getAuthenticatedMember()
        if user.has_permission('cmf.ManagePortal', self.context):
            return True

        elif api.user.is_anonymous():
            return False

        elif self.request.cookies.get(DEBUG_MODE_COOKIE_KEY, False) == 'True':
            return True

        else:
            return False

    def export(self, output='pdf'):
        assembler = getMultiAdapter((self.context, self.request),
                                    IPDFAssembler)

        if output == 'pdf':
            return assembler.build_pdf(**self.get_build_arguments())

        elif output == 'latex':
            return assembler.build_latex(**self.get_build_arguments())

        elif output == 'zip':
            return assembler.build_zip(**self.get_build_arguments())

        else:
            raise ValueError('Unkown output "%s"' % output)

    def get_build_arguments(self):
        return {'request': self.request}


class DebugPDFGeneratorView(BrowserView):
    """This view allows to toggle the pdfgenerator debug mode.
    When the debug mode is enabled, the user is able to select the
    output.
    """

    def __call__(self):
        cookies = self.request.cookies

        self.request.response.setCookie(
            DEBUG_MODE_COOKIE_KEY,
            str(not cookies.get(DEBUG_MODE_COOKIE_KEY,  False) == 'True'),
            quoted=False
        )
        return 'PDFGenerator debug mode is now %s' % (
            self.request.response.cookies.get(DEBUG_MODE_COOKIE_KEY)['value'] == 'True' and 'enabled' or 'disabled')

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.pdfgenerator.interfaces import DEBUG_MODE_SESSION_KEY
from ftw.pdfgenerator.interfaces import IPDFAssembler
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

        elif self.request.SESSION.get(DEBUG_MODE_SESSION_KEY, False):
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
        session = self.request.SESSION

        session[DEBUG_MODE_SESSION_KEY] = not session.get(
            DEBUG_MODE_SESSION_KEY, False)

        return 'PDFGenerator debug mode is now %s' % (
            session.get(DEBUG_MODE_SESSION_KEY) and 'enabled' or 'disabled')

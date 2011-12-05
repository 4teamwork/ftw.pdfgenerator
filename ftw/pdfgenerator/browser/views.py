from Products.Five import BrowserView
from ftw.pdfgenerator.interfaces import IPDFAssembler
from zope.component import getMultiAdapter


class AsPDFView(BrowserView):
    """Export a PDF with default settings. If the user is a Admin (if he
    has Manage portal permission), a additional form will be shown, where
    he can selected the desired output format (PDF, LaTeX only or ZIP).
    """

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
        return user.has_permission('cmf.ManagePortal', self.context)

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

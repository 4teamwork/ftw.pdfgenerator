from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.interfaces import IBuilderFactory
from ftw.pdfgenerator.layout.makolayout import MakoLayoutBase
from ftw.pdfgenerator.view import MakoLaTeXView
from zope.component import getUtility


class BaseStandalonePDFView(ExportPDFView, MakoLayoutBase, MakoLaTeXView):
    """A special standalone PDF view, combining:

    - The export_pdf wizard (ExportPDFView)
    - A LaTeX layout (MakoLayoutBase)
    - A LaTeX view (MakoLaTeXView)

    Extend this class and register it as browser for having a custom PDF
    export which is not recursive. With this approach it is possible to have
    multiple, completely different PDF exports for one single context.
    """

    def __init__(self, context, request):
        # call init on BrowserView, which is the superclass of ExportPDFView
        # pylint: disable=E1003
        # E1003: Bad first argument 'ExportPDFView' given to super class
        super(ExportPDFView, self).__init__(context, request)

        # initialize layout, but with an emty builder. It will be set
        # in get_build_arguments.
        builder = None
        MakoLayoutBase.__init__(self, context, request, builder)

        # initialize the latex view
        layout = self
        MakoLaTeXView.__init__(self, context, request, layout)

    def get_build_arguments(self):
        # ExportPDFView.get_build_arguments
        args = ExportPDFView.get_build_arguments(self)

        # we need to manually create the builder, so that we have a reference
        # to it.
        self.builder = getUtility(IBuilderFactory)()

        # this object is also the layout - tell the assembler
        args.update({'layout': self,
                     'builder': self.builder})

        return args

    def get_views_for(self, obj):
        # MakoLayoutBase.get_views_for

        # Let the layout-part of this object known that this object is
        # also the latex view.
        # We are disable the pre- and post-hooks here!
        return [self]

    def render(self):
        # MakoLaTeXView.render

        # We do not render the view, we use the layout-template for rendering
        # the layout AND the content.
        return ''

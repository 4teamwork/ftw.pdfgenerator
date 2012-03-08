from Products.Archetypes.utils import contentDispositionHeader
from ftw.pdfgenerator.interfaces import IBuilderFactory
from ftw.pdfgenerator.interfaces import ILaTeXLayout
from ftw.pdfgenerator.interfaces import IPDFAssembler
from zope.component import adapts
from zope.component import getMultiAdapter, getUtility
from zope.interface import implements, Interface


class PDFAssembler(object):
    implements(IPDFAssembler)
    adapts(Interface, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._layout = None
        self._view = None
        self._builder = None

    def build_pdf(self, layout=None, builder=None, request=None):
        self._layout = layout
        self._builder = builder

        latex = self.render_latex()
        data = self.get_builder().build(latex)

        if not request:
            return data

        else:
            return self._attach_to_response(request, data, 'pdf')

    def build_latex(self, layout=None, builder=None, request=None):
        self._layout = layout
        self._builder = builder

        latex = self.render_latex()
        self.get_builder().cleanup()
        return latex

    def build_zip(self, layout=None, builder=None, request=None):
        self._layout = layout
        self._builder = builder

        latex = self.render_latex()
        data = self.get_builder().build_zip(latex).read()

        if not request:
            return data

        else:
            return self._attach_to_response(request, data, 'zip')

    def get_builder(self):
        """Returns the IBuilder instance.
        """
        if getattr(self, '_builder', None) is None:
            self._builder = getUtility(IBuilderFactory)()
        return self._builder

    def get_layout(self):
        """Returns the ILaTeXLayout instance.
        """
        if getattr(self, '_layout', None) is None:
            self._layout = getMultiAdapter(
                (self.context, self.request, self.get_builder()),
                ILaTeXLayout)
        return self._layout

    def render_latex(self):
        """Renders the LaTeX for the configured view and layout.
        """
        layout = self.get_layout()
        content_latex = layout.render_latex_for(self.context)
        return layout.render_latex(content_latex)

    def _attach_to_response(self, request, data, extension):
        filename = '%s.%s' % (self.context.id, extension)
        response = request.RESPONSE
        response.setHeader('Content-Type',
                           'application/%s; charset=utf-8' % extension)

        response.setHeader(
            'Content-disposition',
            contentDispositionHeader(
                'attachment', 'utf-8', filename=filename))

        response.write(data)
        return request

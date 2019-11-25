from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.assembler import PDFAssembler
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from ftw.testing import MockTestCase
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface.verify import verifyClass


class TestPDFAssembler(MockTestCase):

    layer = PDFGENERATOR_ZCML_LAYER

    def test_implements_interface(self):
        self.assertTrue(interfaces.IPDFAssembler.implementedBy(PDFAssembler))
        verifyClass(interfaces.IPDFAssembler, PDFAssembler)

    def test_component_registered(self):
        obj = getMultiAdapter((object(), object()), interfaces.IPDFAssembler)
        self.assertEquals(obj.__class__, PDFAssembler)

    def test_build_latex_parameters(self):
        context = object()

        layout = self.mock()
        layout.render_latex_for.return_value = 'content latex'
        layout.render_latex.return_value = 'full latex'

        builder = self.mock()

        obj = getMultiAdapter((context, object()), interfaces.IPDFAssembler)
        latex = obj.build_latex(layout=layout, builder=builder)
        self.assertEqual(latex, 'full latex')
        builder.cleanup.assert_called_once()

    def test_build_latex_parameters_with_fullname_parameter(self):
        context = object()

        layout = self.mock()
        layout.render_latex_for.return_value = 'content latex'
        layout.render_latex.return_value = 'full latex'

        builder = self.mock()

        obj = getMultiAdapter((context, object()), interfaces.IPDFAssembler)
        latex = obj.build_latex(
            layout=layout, builder=builder, filename='test')
        self.assertEqual(latex, 'full latex')
        builder.cleanup.assert_called_once()

    def test_use_filename_when_given(self):
        context = self.mock()
        layout = self.mock()
        layout.render_latex_for.return_value = 'content latex'
        layout.render_latex.return_value = 'full latex'

        builder = self.mock()
        builder.build.return_value = 'the pdf'

        request = self.mock()
        response = self.mock()
        request.RESPONSE = response

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_pdf(layout=layout, builder=builder,
                                       request=request, filename='my_pdf'),
                         request)
        response.setHeader.assert_any_call(
            'Content-Type', 'application/pdf; charset=utf-8')
        response.setHeader.assert_any_call(
            'Content-disposition', 'attachment; filename="my_pdf.pdf"')
        response.write.assert_called_with('the pdf')

    def test_handles_non_ascii_chars_in_filename_correctly(self):
        filename = u'm\xe4i_pdf'
        context = self.mock()
        layout = self.mock()
        layout.render_latex_for.return_value = 'content latex'
        layout.render_latex.return_value = 'full latex'

        builder = self.mock()
        builder.build.return_value = 'the pdf'

        request = self.mock()
        response = self.mock()
        request.RESPONSE = response

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_pdf(layout=layout, builder=builder,
                                       request=request, filename=filename),
                         request)
        response.setHeader.assert_any_call(
            'Content-Type', 'application/pdf; charset=utf-8')
        response.setHeader.assert_any_call(
            'Content-disposition',
            'attachment; filename="{}.pdf"'.format(filename.encode('utf-8')))
        response.write.assert_called_with('the pdf')

    def test_build_pdf_parameters(self):
        context = self.mock()
        context.id = 'theid'

        layout = self.mock()
        layout.render_latex_for.return_value = 'content latex'
        layout.render_latex.return_value = 'full latex'

        builder = self.mock()
        builder.build.return_value = 'the pdf'

        request = self.mock()
        response = self.mock()
        request.RESPONSE = response

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_pdf(layout=layout, builder=builder,
                                       request=request),
                         request)
        response.setHeader.assert_any_call(
            'Content-Type', 'application/pdf; charset=utf-8')
        response.setHeader.assert_any_call(
            'Content-disposition', 'attachment; filename="theid.pdf"')
        response.write.assert_called_with('the pdf')

    def test_build_pdf_with_no_request_returns_data(self):
        context = object()

        layout = self.mock()
        layout.render_latex_for.return_value = 'content latex'
        layout.render_latex.return_value = 'full latex'

        builder = self.mock()
        builder.build.return_value = 'the pdf'

        request = object()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_pdf(layout=layout, builder=builder),
                         'the pdf')

    def test_build_zip_parameters(self):
        context = self.mock()
        context.id = 'theid'

        layout = self.mock()
        layout.render_latex_for.return_value = 'content latex'
        layout.render_latex.return_value = 'full latex'

        builder = self.mock()
        builder.build_zip.return_value.read.return_value = 'the zip'

        request = self.mock()
        response = self.mock()
        request.RESPONSE = response

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_zip(layout=layout, builder=builder,
                                       request=request),
                         request)
        response.setHeader.assert_called()
        response.write.assert_called_with('the zip')

    def test_build_zip_with_filename_parameter(self):
        context = self.mock()
        context.id = 'theid'

        layout = self.mock()
        layout.render_latex_for.return_value = 'content latex'
        layout.render_latex.return_value = 'full latex'

        builder = self.mock()
        builder.build_zip.return_value.read.return_value = 'the zip'

        request = self.mock()
        response = self.mock()
        request.RESPONSE = response

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_zip(layout=layout, builder=builder,
                                       request=request, filename='my_pdf'),
                         request)
        response.setHeader.assert_called()
        response.write.assert_called_with('the zip')

    def test_build_zip_with_no_request_returns_data(self):
        context = object()

        layout = self.mock()
        layout.render_latex_for.return_value = 'content latex'
        layout.render_latex.return_value = 'full latex'

        builder = self.mock()
        builder.build_zip.return_value.read.return_value = 'the zip'

        request = object()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_zip(layout=layout, builder=builder),
                         'the zip')

    def test_get_builder(self):
        factory = self.mock()
        builder = self.mock()
        factory.return_value = builder

        self.mock_utility(factory, interfaces.IBuilderFactory)

        obj = getMultiAdapter((object(), object()), interfaces.IPDFAssembler)
        self.assertEqual(obj.get_builder(), builder)

    def test_get_layout(self):
        context = self.create_dummy()
        request = self.create_dummy()
        builder = self.create_dummy()

        layout = self.mock()
        self.mock_adapter(layout, interfaces.ILaTeXLayout,
                          (Interface, Interface, Interface))
        layout.return_value = layout

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        obj._builder = builder
        self.assertEqual(obj.get_layout(), layout)

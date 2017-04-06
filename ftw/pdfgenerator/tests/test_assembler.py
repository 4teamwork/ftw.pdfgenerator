from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.assembler import PDFAssembler
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from ftw.testing import MockTestCase
from mocker import ARGS
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

        layout = self.mocker.mock()
        self.expect(layout.render_latex_for(context)).result('content latex')
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.cleanup())

        self.replay()

        obj = getMultiAdapter((context, object()), interfaces.IPDFAssembler)
        latex = obj.build_latex(layout=layout, builder=builder)
        self.assertEqual(latex, 'full latex')

    def test_build_latex_parameters_with_fullname_parameter(self):
        context = object()

        layout = self.mocker.mock()
        self.expect(layout.render_latex_for(context)).result('content latex')
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.cleanup())

        self.replay()

        obj = getMultiAdapter((context, object()), interfaces.IPDFAssembler)
        latex = obj.build_latex(
            layout=layout, builder=builder, filename='test')
        self.assertEqual(latex, 'full latex')

    def test_use_filename_when_given(self):
        context = self.mocker.mock()
        layout = self.mocker.mock()
        self.expect(layout.render_latex_for(context)).result('content latex')
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.build('full latex')).result('the pdf')

        request = self.mocker.mock()
        response = self.mocker.mock()
        self.expect(request.RESPONSE).result(response)
        self.expect(response.setHeader(
                'Content-Type', 'application/pdf; charset=utf-8'))
        self.expect(response.setHeader(
                'Content-disposition', 'attachment; filename="my_pdf.pdf"'))
        self.expect(response.write('the pdf'))

        self.replay()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_pdf(layout=layout, builder=builder,
                                       request=request, filename='my_pdf'),
                         request)

    def test_handles_non_ascii_chars_in_filename_correctly(self):
        filename = u'm\xe4i_pdf'
        context = self.mocker.mock()
        layout = self.mocker.mock()
        self.expect(layout.render_latex_for(context)).result('content latex')
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.build('full latex')).result('the pdf')

        request = self.mocker.mock()
        response = self.mocker.mock()
        self.expect(request.RESPONSE).result(response)
        self.expect(response.setHeader(
                'Content-Type', 'application/pdf; charset=utf-8'))

        self.expect(response.setHeader(
            'Content-disposition',
            'attachment; filename="{}.pdf"'.format(filename.encode('utf-8'))))
        self.expect(response.write('the pdf'))

        self.replay()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_pdf(layout=layout, builder=builder,
                                       request=request, filename=filename),
                         request)

    def test_build_pdf_parameters(self):
        context = self.mocker.mock()
        self.expect(context.id).result('theid')

        layout = self.mocker.mock()
        self.expect(layout.render_latex_for(context)).result('content latex')
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.build('full latex')).result('the pdf')

        request = self.mocker.mock()
        response = self.mocker.mock()
        self.expect(request.RESPONSE).result(response)
        self.expect(response.setHeader(
                'Content-Type', 'application/pdf; charset=utf-8'))
        self.expect(response.setHeader(
                'Content-disposition', 'attachment; filename="theid.pdf"'))
        self.expect(response.write('the pdf'))

        self.replay()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_pdf(layout=layout, builder=builder,
                                       request=request),
                         request)

    def test_build_pdf_with_no_request_returns_data(self):
        context = object()

        layout = self.mocker.mock()
        self.expect(layout.render_latex('content latex')).result(
            'full latex')
        self.expect(layout.render_latex_for(context)).result('content latex')

        builder = self.mocker.mock()
        self.expect(builder.build('full latex')).result('the pdf')

        request = object()

        self.replay()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_pdf(layout=layout, builder=builder),
                         'the pdf')

    def test_build_zip_parameters(self):
        context = self.mocker.mock()
        self.expect(context.id, 'theid')

        layout = self.mocker.mock()
        self.expect(layout.render_latex_for(context)).result('content latex')
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.build_zip('full latex').read()).result('the zip')

        request = self.mocker.mock()
        response = self.mocker.mock()
        self.expect(request.RESPONSE).result(response)
        self.expect(response.setHeader(ARGS)).count(1, None)
        self.expect(response.write('the zip'))

        self.replay()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_zip(layout=layout, builder=builder,
                                       request=request),
                         request)

    def test_build_zip_with_filename_parameter(self):
        context = self.stub()
        self.expect(context.id, 'theid')

        layout = self.mocker.mock()
        self.expect(layout.render_latex_for(context)).result('content latex')
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.build_zip('full latex').read()).result('the zip')

        request = self.mocker.mock()
        response = self.mocker.mock()
        self.expect(request.RESPONSE).result(response)
        self.expect(response.setHeader(ARGS)).count(1, None)
        self.expect(response.write('the zip'))

        self.replay()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_zip(layout=layout, builder=builder,
                                       request=request, filename='my_pdf'),
                         request)

    def test_build_zip_with_no_request_returns_data(self):
        context = object()

        layout = self.mocker.mock()
        self.expect(layout.render_latex_for(context)).result('content latex')
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.build_zip('full latex').read()).result('the zip')

        request = object()

        self.replay()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_zip(layout=layout, builder=builder),
                         'the zip')

    def test_get_builder(self):
        factory = self.mocker.mock()
        builder = self.mocker.mock()
        self.expect(factory()).result(builder)

        self.mock_utility(factory, interfaces.IBuilderFactory)

        self.replay()

        obj = getMultiAdapter((object(), object()), interfaces.IPDFAssembler)
        self.assertEqual(obj.get_builder(), builder)
        self.assertEqual(obj.get_builder(), obj.get_builder())

    def test_get_layout(self):
        context = self.create_dummy()
        request = self.create_dummy()
        builder = self.create_dummy()

        layout = self.mocker.mock()
        self.mock_adapter(layout, interfaces.ILaTeXLayout,
                          (Interface, Interface, Interface))
        self.expect(layout(context, request, builder)).result(layout)

        self.replay()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        obj._builder = builder
        self.assertEqual(obj.get_layout(), layout)

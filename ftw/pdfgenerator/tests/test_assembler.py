from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.assembler import PDFAssembler
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from mocker import ARGS
from plone.mocktestcase import MockTestCase
from zope.component import getMultiAdapter
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
        view = self.mocker.mock()
        self.expect(view.render()).result('content latex')

        layout = self.mocker.mock()
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.cleanup())

        self.replay()

        obj = getMultiAdapter((object(), object()), interfaces.IPDFAssembler)
        latex = obj.build_latex(layout=layout, view=view, builder=builder)
        self.assertEqual(latex, 'full latex')

    def test_build_pdf_parameters(self):
        view = self.mocker.mock()
        self.expect(view.render()).result('content latex')

        layout = self.mocker.mock()
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.build('full latex')).result('the pdf')

        context = self.mocker.mock()
        self.expect(context.id(), 'theid')

        request = self.mocker.mock()
        response = self.mocker.mock()
        self.expect(request.RESPONSE).result(response)
        self.expect(response.setHeader(ARGS)).count(1, None)
        self.expect(response.write('the pdf'))

        self.replay()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_pdf(layout=layout, view=view,
                                       builder=builder, request=request),
                         request)

    def test_build_zip_parameters(self):
        view = self.mocker.mock()
        self.expect(view.render()).result('content latex')

        layout = self.mocker.mock()
        self.expect(layout.render_latex('content latex')).result(
            'full latex')

        builder = self.mocker.mock()
        self.expect(builder.build_zip('full latex').read()).result('the zip')

        context = self.mocker.mock()
        self.expect(context.id(), 'theid')

        request = self.mocker.mock()
        response = self.mocker.mock()
        self.expect(request.RESPONSE).result(response)
        self.expect(response.setHeader(ARGS)).count(1, None)
        self.expect(response.write('the zip'))

        self.replay()

        obj = getMultiAdapter((context, request), interfaces.IPDFAssembler)
        self.assertEqual(obj.build_zip(layout=layout, view=view,
                                       builder=builder, request=request),
                         request)

    def test_get_builder(self):
        factory = self.mocker.mock()
        builder = self.mocker.mock()
        self.expect(factory()).result(builder)

        self.mock_utility(factory, interfaces.IBuilderFactory)

        self.replay()

        obj = getMultiAdapter((object(), object()), interfaces.IPDFAssembler)
        self.assertEqual(obj.get_builder(), builder)
        self.assertEqual(obj.get_builder(), obj.get_builder())

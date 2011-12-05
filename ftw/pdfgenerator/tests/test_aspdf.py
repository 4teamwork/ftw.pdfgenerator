from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.browser.views import AsPDFView
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from mocker import ANY
from plone.mocktestcase import MockTestCase
from zope.component import getMultiAdapter
from zope.interface import Interface, directlyProvides
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestAsPDFView(MockTestCase):

    layer = PDFGENERATOR_ZCML_LAYER

    def mock_allow_alternate_output(self, result_value):
        request = self.mocker.mock()
        context = self.mocker.mock()
        user = self.mocker.mock()
        self.expect(
            context.portal_membership.getAuthenticatedMember()).result(user)

        self.expect(user.has_permission('cmf.ManagePortal', context)).result(
            result_value)

        return context, request

    def test_component_registered(self):
        request = self.create_dummy()
        directlyProvides(request, IDefaultBrowserLayer)
        aspdf = getMultiAdapter((object(), request), name='as_pdf')
        self.assertTrue(isinstance(aspdf, AsPDFView))

    def test_get_build_arguments(self):
        context = object()
        request = object()
        aspdf = AsPDFView(context, request)
        self.assertEqual(aspdf.get_build_arguments(), {'request': request})

    def test_export_as_pdf(self):
        context = object()
        request = object()

        assembler = self.mocker.mock()
        self.mock_adapter(assembler, interfaces.IPDFAssembler,
                          (Interface, Interface))
        self.expect(assembler(ANY, ANY)).result(assembler)
        self.expect(assembler.build_pdf(
                request=request)).result(request)

        self.replay()

        aspdf = AsPDFView(context, request)
        self.assertEqual(aspdf.export(output='pdf'), request)

    def test_export_as_latex(self):
        context = object()
        request = object()

        assembler = self.mocker.mock()
        self.mock_adapter(assembler, interfaces.IPDFAssembler,
                          (Interface, Interface))
        self.expect(assembler(ANY, ANY)).result(assembler)
        self.expect(assembler.build_latex(
                request=request)).result(request)

        self.replay()

        aspdf = AsPDFView(context, request)
        self.assertEqual(aspdf.export(output='latex'), request)

    def test_export_as_zip(self):
        context = object()
        request = object()

        assembler = self.mocker.mock()
        self.mock_adapter(assembler, interfaces.IPDFAssembler,
                          (Interface, Interface))
        self.expect(assembler(ANY, ANY)).result(assembler)
        self.expect(assembler.build_zip(
                request=request)).result(request)

        self.replay()

        aspdf = AsPDFView(context, request)
        self.assertEqual(aspdf.export(output='zip'), request)

    def test_export_with_unkown_output(self):
        context = object()
        request = object()

        assembler = self.mocker.mock()
        self.mock_adapter(assembler, interfaces.IPDFAssembler,
                          (Interface, Interface))
        self.expect(assembler(ANY, ANY)).result(assembler)

        self.replay()

        aspdf = AsPDFView(context, request)

        with self.assertRaises(ValueError) as cm:
            self.assertEqual(aspdf.export(output='foo'), request)

        self.assertEqual(str(cm.exception),
                         'Unkown output "foo"')

    def test_allow_alternate_output_True(self):
        context, request = self.mock_allow_alternate_output(True)

        self.replay()

        aspdf = AsPDFView(context, request)
        self.assertEqual(aspdf.allow_alternate_output(), True)

    def test_allow_alternate_output_False(self):
        context, request = self.mock_allow_alternate_output(False)

        self.replay()

        aspdf = AsPDFView(context, request)
        self.assertEqual(aspdf.allow_alternate_output(), False)

    def test_call_renders_template_if_admin(self):
        context, request = self.mock_allow_alternate_output(True)

        aspdf = self.mocker.patch(AsPDFView(context, request), spec=False)
        self.expect(request.get('submitted', False)).result(False)
        self.expect(aspdf.index()).result('rendered html')

        self.replay()

        self.assertEqual(aspdf(), 'rendered html')

    def test_call_exports_if_not_admin(self):
        context, request = self.mock_allow_alternate_output(False)

        aspdf = self.mocker.patch(AsPDFView(context, request))
        self.expect(aspdf.export()).result('pdf')

        self.replay()

        self.assertEqual(aspdf(), 'pdf')

    def test_call_uses_output_from_request_if_admin(self):
        context, request = self.mock_allow_alternate_output(True)
        self.expect(request.get('submitted', False)).result(True)
        self.expect(request.get('output')).result('latex')

        aspdf = self.mocker.patch(AsPDFView(context, request))
        self.expect(aspdf.export('latex')).result('latex code')

        self.replay()

        self.assertEqual(aspdf(), 'latex code')

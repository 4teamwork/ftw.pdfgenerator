from ftw.pdfgenerator import interfaces
from ftw.pdfgenerator.browser.views import ExportPDFView
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from ftw.testing import MockTestCase
from mock import patch
from zope.component import getMultiAdapter
from zope.interface import Interface, directlyProvides
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestAsPDFView(MockTestCase):

    layer = PDFGENERATOR_ZCML_LAYER

    def mock_allow_alternate_output(self, result_value, debug_mode=False):
        request = self.mock()
        context = self.mock()
        user = self.mock()
        context.portal_membership.getAuthenticatedMember.return_value = user

        user.has_permission.return_value = result_value

        session = self.mock()
        session.get.return_value = debug_mode
        request.SESSION = session

        return context, request

    def test_component_registered(self):
        request = self.create_dummy()
        directlyProvides(request, IDefaultBrowserLayer)
        aspdf = getMultiAdapter((object(), request), name='export_pdf')
        self.assertTrue(isinstance(aspdf, ExportPDFView))

    def test_get_build_arguments(self):
        context = object()
        request = object()
        aspdf = ExportPDFView(context, request)
        self.assertEqual(aspdf.get_build_arguments(), {'request': request})

    def test_export_as_pdf(self):
        context = object()
        request = object()

        assembler = self.mock()
        self.mock_adapter(assembler, interfaces.IPDFAssembler,
                          (Interface, Interface))
        assembler.return_value = assembler
        assembler.build_pdf.return_value = request

        aspdf = ExportPDFView(context, request)
        self.assertEqual(aspdf.export(output='pdf'), request)

    def test_export_as_latex(self):
        context = object()
        request = object()

        assembler = self.mock()
        self.mock_adapter(assembler, interfaces.IPDFAssembler,
                          (Interface, Interface))
        assembler.return_value = assembler
        assembler.build_latex.return_value = request

        aspdf = ExportPDFView(context, request)
        self.assertEqual(aspdf.export(output='latex'), request)

    def test_export_as_zip(self):
        context = object()
        request = object()

        assembler = self.mock()
        self.mock_adapter(assembler, interfaces.IPDFAssembler,
                          (Interface, Interface))
        assembler.return_value = assembler
        assembler.build_zip.return_value = request

        aspdf = ExportPDFView(context, request)
        self.assertEqual(aspdf.export(output='zip'), request)

    def test_export_with_unkown_output(self):
        context = object()
        request = object()

        assembler = self.mock()
        self.mock_adapter(assembler, interfaces.IPDFAssembler,
                          (Interface, Interface))
        assembler.return_value = assembler

        aspdf = ExportPDFView(context, request)

        with self.assertRaises(ValueError) as cm:
            self.assertEqual(aspdf.export(output='foo'), request)

        self.assertEqual(str(cm.exception),
                         'Unkown output "foo"')

    def test_allow_alternate_output_True(self):
        context, request = self.mock_allow_alternate_output(True)

        aspdf = ExportPDFView(context, request)
        self.assertEqual(aspdf.allow_alternate_output(), True)

    @patch('plone.api.user.is_anonymous')
    def test_allow_alternate_output_False(self, is_anonymous):
        is_anonymous.return_value = False

        context, request = self.mock_allow_alternate_output(False)

        aspdf = ExportPDFView(context, request)
        self.assertEqual(aspdf.allow_alternate_output(), False)

    @patch('plone.api.user.is_anonymous')
    def test_allow_alternate_output_in_debug_mode_False(self, is_anonymous):
        is_anonymous.return_value = False
        context, request = self.mock_allow_alternate_output(False, True)

        aspdf = ExportPDFView(context, request)
        self.assertEqual(aspdf.allow_alternate_output(), True)

    @patch('plone.api.user.is_anonymous')
    def test_do_not_allow_alternate_output_for_anonymous(self, is_anonymous):
        is_anonymous.return_value = True

        context, request = self.mock_allow_alternate_output(False)

        aspdf = ExportPDFView(context, request)
        self.assertEqual(aspdf.allow_alternate_output(), False)

    def test_call_renders_template_if_admin(self):
        context, request = self.mock_allow_alternate_output(True)

        with patch(
            'ftw.pdfgenerator.tests.test_export.ExportPDFView.index'
        ) as mocked_index:
            mocked_index.return_value = 'rendered html'
            request.get.return_value = False
            aspdf = ExportPDFView(context, request)
            self.assertEqual(aspdf(), 'rendered html')

    @patch('plone.api.user.is_anonymous')
    def test_call_exports_if_not_admin(self, is_anonymous):
        is_anonymous.return_value = False
        context, request = self.mock_allow_alternate_output(False)
        request_params = {
            'submitted': True,
            'output': 'pdf',
        }
        with patch(
            'ftw.pdfgenerator.tests.test_export.ExportPDFView.export'
        ) as mocked_export:
            mocked_export.return_value = 'pdf'
            request.get.side_effect = (
                lambda name, default=None: request_params.get(name, default)
            )
            aspdf = ExportPDFView(context, request)
            self.assertEqual(aspdf(), 'pdf')

    def test_call_uses_output_from_request_if_admin(self):
        context, request = self.mock_allow_alternate_output(True)
        request_params = {
            'submitted': True,
            'output': 'latex',
        }

        with patch(
            'ftw.pdfgenerator.tests.test_export.ExportPDFView.export'
        ) as mocked_export:
            mocked_export.return_value = 'latex code'
            request.get.side_effect = (
                lambda name, default=None: request_params.get(name, default)
            )
            aspdf = ExportPDFView(context, request)
            self.assertEqual(aspdf(), 'latex code')

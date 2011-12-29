from ftw.pdfgenerator.browser.standalone import BaseStandalonePDFView
from ftw.pdfgenerator.interfaces import IBuilder
from ftw.pdfgenerator.testing import PREDEFINED_BUILD_DIRECTORY_LAYER
from unittest2 import TestCase


class TestBaseStandalonePDFView(TestCase):

    layer = PREDEFINED_BUILD_DIRECTORY_LAYER

    def test_view_attributes(self):
        context = object()
        request = object()

        view = BaseStandalonePDFView(context, request)
        self.assertEquals(view.context, context)
        self.assertEquals(view.request, request)

    def test_view_is_layout(self):
        context = object()
        request = object()

        view = BaseStandalonePDFView(context, request)
        self.assertEquals(view.layout, view)

    def test_build_arguments(self):
        context = object()
        request = object()

        view = BaseStandalonePDFView(context, request)

        args = view.get_build_arguments()
        self.assertEquals(set(args.keys()),
                          set(('request', 'layout', 'builder')))

        self.assertEquals(view, args['layout'])
        self.assertEquals(view.builder, args['builder'])
        self.assertEquals(request, args['request'])

        self.assertTrue(IBuilder.providedBy(view.builder))

    def test_view_is_latex_view(self):
        context = object()
        request = object()

        view = BaseStandalonePDFView(context, request)

        self.assertEquals(view.get_views_for(context), [view])

    def test_view_does_not_render(self):
        context = object()
        request = object()

        view = BaseStandalonePDFView(context, request)

        self.assertEqual(view.render(), '')

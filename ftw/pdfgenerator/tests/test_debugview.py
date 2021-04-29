from ftw.pdfgenerator.browser.views import DebugPDFGeneratorView
from ftw.pdfgenerator.interfaces import DEBUG_MODE_COOKIE_KEY
from ftw.pdfgenerator.testing import PDFGENERATOR_FUNCTIONAL
from ftw.testbrowser import browsing
from unittest import TestCase
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest


class TestDebugPDFGeneratorView(TestCase):

    layer = PDFGENERATOR_FUNCTIONAL

    def test_component_registered(self):
        request = TestRequest()
        view = getMultiAdapter((object(), request), name='debug-pdf')
        self.assertTrue(isinstance(view, DebugPDFGeneratorView))

    @browsing
    def test_toggle(self, browser):

        browser.visit()
        self.assertIsNone(browser.cookies.get(DEBUG_MODE_COOKIE_KEY))

        browser.visit(view='debug-pdf')
        self.assertEquals(browser.contents, 'PDFGenerator debug mode is now enabled')
        self.assertEquals(browser.cookies.get(DEBUG_MODE_COOKIE_KEY)['value'], 'True')

        browser.visit(view='debug-pdf')
        self.assertEquals(browser.contents, 'PDFGenerator debug mode is now disabled')
        self.assertEquals(browser.cookies.get(DEBUG_MODE_COOKIE_KEY)['value'], 'False')

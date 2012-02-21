from ftw.pdfgenerator.browser.views import DebugPDFGeneratorView
from ftw.pdfgenerator.interfaces import DEBUG_MODE_SESSION_KEY
from ftw.pdfgenerator.testing import PDFGENERATOR_ZCML_LAYER
from plone.mocktestcase.dummy import Dummy
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.interface import directlyProvides
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class TestDebugPDFGeneratorView(TestCase):

    layer = PDFGENERATOR_ZCML_LAYER

    def test_component_registered(self):
        request = Dummy()
        directlyProvides(request, IDefaultBrowserLayer)
        view = getMultiAdapter((object(), request), name='debug-pdf')
        self.assertTrue(isinstance(view, DebugPDFGeneratorView))

    def test_toggle(self):
        session = {}
        request = Dummy(SESSION=session)
        directlyProvides(request, IDefaultBrowserLayer)

        view = getMultiAdapter((object(), request), name='debug-pdf')

        self.assertEquals(session.get(DEBUG_MODE_SESSION_KEY, False), False)

        self.assertEquals(view(), 'PDFGenerator debug mode is now enabled')
        self.assertEquals(session.get(DEBUG_MODE_SESSION_KEY, False), True)

        self.assertEquals(view(), 'PDFGenerator debug mode is now disabled')
        self.assertEquals(session.get(DEBUG_MODE_SESSION_KEY, False), False)

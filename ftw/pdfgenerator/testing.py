from plone.testing import Layer
from plone.testing import zca
from zope.configuration import xmlconfig
import ftw.pdfgenerator


class PDFGeneratorZCMLLayer(Layer):
    """A layer which only sets up the zcml, but does not start a zope instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def testSetUp(self):
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))

        xmlconfig.file('configure.zcml', ftw.pdfgenerator,
                       context=self['configurationContext'])

    def testTearDown(self):
        del self['configurationContext']


PDFGENERATOR_ZCML_LAYER = PDFGeneratorZCMLLayer()

from ftw.pdfgenerator.interfaces import IConfig
from ftw.testing.layer import ComponentRegistryLayer
from ftw.testing.testcase import Dummy
from mock import Mock
from plone.testing import Layer
from zope.component import getGlobalSiteManager
from zope.component import provideUtility
from zope.component.hooks import setSite
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.interface import alsoProvides
import os
import shutil
import tempfile


class PDFGeneratorZCMLLayer(ComponentRegistryLayer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    def setUp(self):
        super(PDFGeneratorZCMLLayer, self).setUp()
        import ftw.pdfgenerator
        self.load_zcml_file('test.zcml', ftw.pdfgenerator.tests)
        self.load_zcml_file('configure.zcml', ftw.pdfgenerator)


PDFGENERATOR_ZCML_LAYER = PDFGeneratorZCMLLayer()


class ZCMLWithSiteLayer(Layer):
    """A layer with loaded zcml and a global site.
    """

    defaultBases = (PDFGENERATOR_ZCML_LAYER,)

    def testSetUp(self):
        setSite(self._create_site_with_request())

    def testTearDown(self):
        setSite(None)

    def _create_site_with_request(self):
        request = Dummy(getPreferredLanguages=lambda: [])
        alsoProvides(request, IUserPreferredLanguages)
        site = Dummy(REQUEST=request,
                     getSiteManager=getGlobalSiteManager)

        return site


ZCML_WITH_SITE_LAYER = ZCMLWithSiteLayer()


class PredefinedBuildDirectoryLayer(Layer):

    defaultBases = (PDFGENERATOR_ZCML_LAYER,)

    def setUp(self):
        self.builddir = os.path.join(tempfile.mkdtemp('test-builder'),
                                     'build')

        self.config = Mock()
        self.config.get_build_directory.return_value = self.builddir
        provideUtility(provides=IConfig, component=self.config)

    def testSetUp(self):
        self.config.remove_build_directory = True
        os.mkdir(self.builddir)

    def testTearDown(self):
        if os.path.exists(self.builddir):
            shutil.rmtree(self.builddir)


PREDEFINED_BUILD_DIRECTORY_LAYER = PredefinedBuildDirectoryLayer()

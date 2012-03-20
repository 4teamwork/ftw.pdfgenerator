from ftw.pdfgenerator.config import DefaultConfig
from ftw.pdfgenerator.interfaces import IConfig
from ftw.testing.layer import ComponentRegistryLayer
from mocker import Mocker, expect
from plone.testing import Layer
from zope.component import provideUtility
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


class PredefinedBuildDirectoryLayer(Layer):

    defaultBases = (PDFGENERATOR_ZCML_LAYER,)

    def setUp(self):
        self.testcase_mocker = Mocker()
        self.builddir = os.path.join(tempfile.mkdtemp('test-builder'),
                                     'build')

        self.config = self.testcase_mocker.proxy(
            DefaultConfig(),
            spec=None,
            count=False)
        expect(self.config.get_build_directory()).result(self.builddir)

        self.testcase_mocker.replay()

    def testSetUp(self):
        provideUtility(provides=IConfig, component=self.config)
        os.mkdir(self.builddir)

    def tearDown(self):
        self.testcase_mocker.verify()
        self.testcase_mocker.restore()

    def testTearDown(self):
        if os.path.exists(self.builddir):
            shutil.rmtree(self.builddir)


PREDEFINED_BUILD_DIRECTORY_LAYER = PredefinedBuildDirectoryLayer()

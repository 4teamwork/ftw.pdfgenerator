from ftw.pdfgenerator.config import DefaultConfig
from ftw.pdfgenerator.interfaces import IConfig
from mocker import Mocker, expect
from plone.testing import Layer
from plone.testing import zca
from zope.component import provideUtility
from zope.configuration import xmlconfig
import os
import shutil
import tempfile


class PDFGeneratorZCMLLayer(Layer):
    """A layer which only sets up the zcml, but does not start a zope
    instance.
    """

    defaultBases = (zca.ZCML_DIRECTIVES,)

    def testSetUp(self):
        self['configurationContext'] = zca.stackConfigurationContext(
            self.get('configurationContext'))

        import ftw.pdfgenerator.tests
        xmlconfig.file('test.zcml', ftw.pdfgenerator.tests,
                       context=self['configurationContext'])

        import ftw.pdfgenerator
        xmlconfig.file('configure.zcml', ftw.pdfgenerator,
                       context=self['configurationContext'])

    def testTearDown(self):
        del self['configurationContext']


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

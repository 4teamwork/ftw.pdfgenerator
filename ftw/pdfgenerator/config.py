from ftw.pdfgenerator.interfaces import IConfig
from zope.interface import implements
import tempfile


class DefaultConfig(object):
    implements(IConfig)

    remove_build_directory = True

    def get_build_directory(self):
        return tempfile.mkdtemp(prefix='ftw.pdfgenerator_')

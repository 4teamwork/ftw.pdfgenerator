from StringIO import StringIO
from ftw.pdfgenerator.exceptions import BuildTerminated, PDFBuildFailed
from ftw.pdfgenerator.interfaces import IBuilder, IConfig
from zipfile import ZipFile
from zope.component import getUtility
from zope.interface import implements
import os
import shlex
import shutil
import subprocess


class Builder(object):
    implements(IBuilder)

    def __init__(self):
        self.config = getUtility(IConfig)
        self.build_directory = self.config.get_build_directory()
        self._terminated = False

    def add_file(self, filename, data):
        if self._terminated:
            raise BuildTerminated('The build is already terminated.')

        path = os.path.join(self.build_directory, filename)
        file_ = open(path, 'wb')
        file_.write(data)
        file_.close()

    def build(self, latex):
        if self._terminated:
            raise BuildTerminated('The build is already terminated.')

        try:
            pdf_path = self._build_pdf(latex)

        except PDFBuildFailed:
            self._cleanup_build()
            raise

        else:
            pdf_file = open(pdf_path, 'rb')
            data = pdf_file.read()
            pdf_file.close()
            self._cleanup_build()
            return data

    def build_zip(self, latex):
        if self._terminated:
            raise BuildTerminated('The build is already terminated.')

        try:
            self._build_pdf(latex)

        except PDFBuildFailed:
            self._cleanup_build()
            raise

        else:
            data = StringIO()
            zip = ZipFile(data, 'w')

            for filename in os.listdir(self.build_directory):
                zip.write(os.path.join(self.build_directory, filename),
                          filename)

            zip.close()
            data.seek(0)

            self._cleanup_build()
            return data

    def _build_pdf(self, latex):
        """Build the pdf in the build_directory and return the path to
        the pdf.
        """
        latex_path = os.path.join(self.build_directory, 'export.tex')
        pdf_path = os.path.join(self.build_directory, 'export.pdf')

        assert not os.path.exists(latex_path), 'export.tex already exists'
        assert not os.path.exists(pdf_path), 'export.pdf already exists'

        latex_file = open(latex_path, 'w')
        latex_file.write(latex)
        latex_file.close()

        cmd = 'pdflatex --interaction=nonstopmode %s' % latex_path
        exitcode, stdout, stderr = self._execute(cmd)

        if exitcode > 0:
            raise PDFBuildFailed(stderr)

        return pdf_path

    def _cleanup_build(self):
        self._terminated = True

        if self.config.remove_build_directory:
            shutil.rmtree(self.build_directory)

    def _execute(self, cmd):
        proc = subprocess.Popen(shlex.split(cmd),
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                cwd=self.build_directory)
        output, errors = proc.communicate()
        return proc.poll(), output, errors


def builder_factory():
    return Builder()

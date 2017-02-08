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


RESOURCES_DIR = os.path.abspath(os.path.join(__file__, '..', 'resources'))


class Builder(object):
    implements(IBuilder)

    def __init__(self):
        self.config = getUtility(IConfig)
        self.build_directory = self.config.get_build_directory()
        self._terminated = False
        self._aux_data = None
        self._rerun_limit = 10

    def add_file(self, filename, data):
        if self._terminated:
            raise BuildTerminated('The build is already terminated.')

        path = os.path.join(self.build_directory, filename)
        with open(path, 'wb') as fio:
            if hasattr(data, 'read'):
                shutil.copyfileobj(data, fio)
            else:
                fio.write(data)

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
            pass
        data = StringIO()
        zip_file = ZipFile(data, 'w')

        for filename in os.listdir(self.build_directory):
            zip_file.write(os.path.join(self.build_directory, filename),
                      filename)

        zip_file.close()
        data.seek(0)

        self._cleanup_build()
        return data

    def cleanup(self):
        if not self._terminated:
            self._cleanup_build()

    def _build_pdf(self, latex):
        """Build the pdf in the build_directory and return the path to
        the pdf.
        """
        latex_path = os.path.join(self.build_directory, 'export.tex')
        pdf_path = os.path.join(self.build_directory, 'export.pdf')

        assert not os.path.exists(latex_path), 'export.tex already exists'
        assert not os.path.exists(pdf_path), 'export.pdf already exists'

        latex_file = open(latex_path, 'w')
        if isinstance(latex, unicode):
            latex = latex.encode('utf-8')
        latex_file.write(latex)
        latex_file.close()

        self._run_pdflatex(latex_path)
        if self._makeindex():
            self._run_pdflatex(latex_path)

        if not os.path.exists(pdf_path):
            raise PDFBuildFailed('PDF missing.')

        return pdf_path

    def _run_pdflatex(self, latex_path):
        self._aux_data = None
        cmd = 'pdflatex --interaction=nonstopmode %s' % latex_path
        stdout = ''
        while self._rerun_required(stdout):
            _exitcode, stdout, _stderr = self._execute(cmd)

    def _makeindex(self):
        idx_path = os.path.join(self.build_directory, 'export.idx')
        if not os.path.exists(idx_path):
            return False

        # When the makeindex arguments are too long, we might get a
        # buffer oferflow.
        # For avoiding this, we copy the "umlaut.ist" to the export directory.
        umlaut_ist_path = os.path.join(RESOURCES_DIR, 'umlaut.ist')
        shutil.copyfile(umlaut_ist_path, os.path.join(self.build_directory, 'umlaut.ist'))
        self._execute('makeindex -g -s umlaut.ist export')
        return True

    def _rerun_required(self, stdout):
        if self._rerun_limit == 0:
            raise PDFBuildFailed('Maximum pdf build limit reached.')

        self._rerun_limit -= 1

        previous_aux_data = self._aux_data

        self._aux_data = []
        for filename in os.listdir(self.build_directory):
            if filename.endswith('.aux'):
                path = os.path.join(self.build_directory, filename)
                file_ = open(path)
                self._aux_data.append(file_.read())
                file_.close()

        if 'Rerun to get' in stdout:
            return True

        elif previous_aux_data is None:
            return True

        elif previous_aux_data != self._aux_data:
            return True

        else:
            return False

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

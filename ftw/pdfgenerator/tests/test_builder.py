# pylint: disable=W0212, W0201
# W0212: Access to a protected member of a client class
# W0201: Attribute defined outside __init__

from ftw.pdfgenerator.builder import Builder
from ftw.pdfgenerator.exceptions import BuildTerminated, PDFBuildFailed
from ftw.pdfgenerator.interfaces import IBuilder, IBuilderFactory
from ftw.pdfgenerator.testing import PREDEFINED_BUILD_DIRECTORY_LAYER
from ftw.testing import MockTestCase
from mocker import MATCH, ANY
from StringIO import StringIO
from zipfile import ZipFile
from zope.component import getUtility
from zope.interface.verify import verifyClass
import os


class TestBuilder(MockTestCase):

    layer = PREDEFINED_BUILD_DIRECTORY_LAYER

    def setUp(self):
        super(TestBuilder, self).setUp()
        self.builddir = self.layer.builddir

    def test_utility_is_factory(self):
        factory = getUtility(IBuilderFactory)
        self.assertFalse(IBuilder.implementedBy(factory))
        self.assertEqual(factory().__class__, Builder)

    def test_factory_returns_builder(self):
        factory = getUtility(IBuilderFactory)
        builder = factory()
        self.assertTrue(IBuilder.providedBy(builder))
        verifyClass(IBuilder, Builder)

    def test_builder_implements_interface(self):
        self.assertTrue(IBuilder.implementedBy(Builder))
        verifyClass(IBuilder, Builder)

    def test_build_directory_is_mocked_in_test_setup(self):
        factory = getUtility(IBuilderFactory)
        builder = factory()
        self.assertEqual(builder.build_directory, self.builddir)

    def test_add_file(self):
        builder = getUtility(IBuilderFactory)()
        builder.add_file('foo.txt', 'Foo\nBar')

        self.assertTrue(os.path.exists(self.builddir))
        filepath = os.path.join(self.builddir, 'foo.txt')
        self.assertTrue(os.path.exists(filepath),
                        'File not found: {0}'.format(filepath))
        self.assertEqual(open(filepath).read(), 'Foo\nBar')

    def test_add_file_by_file_object(self):
        builder = getUtility(IBuilderFactory)()
        builder.add_file('foo.txt', StringIO('Foo\nBar'))

        self.assertTrue(os.path.exists(self.builddir))
        filepath = os.path.join(self.builddir, 'foo.txt')
        self.assertTrue(os.path.exists(filepath),
                        'File not found: {0}'.format(filepath))
        self.assertEqual(open(filepath).read(), 'Foo\nBar')

    def test_terminated_exception_raised(self):
        builder = self.mocker.patch(getUtility(IBuilderFactory)())
        fake_pdf_path = os.path.join(self.builddir, 'export.pdf')
        fake_pdf = open(fake_pdf_path, 'w')
        fake_pdf.write('the pdf')
        fake_pdf.close()

        self.expect(builder._build_pdf(ANY)).result(fake_pdf_path)
        self.replay()

        builder.build('LaTeX')

        with self.assertRaises(BuildTerminated) as cm:
            builder.add_file('foo.txt', 'Foo\nBar')
        self.assertEqual(str(cm.exception),
                         'The build is already terminated.')

        with self.assertRaises(BuildTerminated) as cm:
            builder.build('LaTeX')
        self.assertEqual(str(cm.exception),
                         'The build is already terminated.')

        with self.assertRaises(BuildTerminated) as cm:
            builder.build_zip('LaTeX')
        self.assertEqual(str(cm.exception),
                         'The build is already terminated.')

    def test_build_removes_directory(self):
        builder = self.mocker.patch(getUtility(IBuilderFactory)())

        def execute_mock(cmd):
            self.assertEqual(
                open(os.path.join(self.builddir, 'export.tex')).read(),
                'LaTeX Code')

            pdf = open(os.path.join(self.builddir, 'export.pdf'), 'w')
            pdf.write('Rendered PDF')
            pdf.close()
            return 0, '', ''

        self.expect(
            builder._execute(
                MATCH(lambda cmd: cmd.startswith('pdflatex ')))
            ).call(execute_mock)

        self.replay()

        self.assertTrue(builder.config.remove_build_directory)
        self.assertEqual(builder.build('LaTeX Code'), 'Rendered PDF')
        self.assertFalse(os.path.exists(builder.build_directory))

    def test_build_does_not_remove_directory_if_disabled(self):
        builder = self.mocker.patch(getUtility(IBuilderFactory)())
        self.expect(builder.config.remove_build_directory).result(False)

        def execute_mock(cmd):
            self.assertEqual(
                open(os.path.join(self.builddir, 'export.tex')).read(),
                'LaTeX Code')

            pdf = open(os.path.join(self.builddir, 'export.pdf'), 'w')
            pdf.write('Rendered PDF')
            pdf.close()
            return 0, '', ''

        self.expect(
            builder._execute(
                MATCH(lambda cmd: cmd.startswith('pdflatex ')))
            ).call(execute_mock)

        self.replay()

        self.assertEqual(builder.build('LaTeX Code'), 'Rendered PDF')
        self.assertTrue(os.path.exists(builder.build_directory))

    def test_build_zip_returns_valid_zip_file_as_stream(self):
        builder = self.mocker.patch(getUtility(IBuilderFactory)())

        def execute_mock(cmd):
            self.assertEqual(
                open(os.path.join(self.builddir, 'export.tex')).read(),
                'LaTeX Code')

            pdf = open(os.path.join(self.builddir, 'export.pdf'), 'w')
            pdf.write('Rendered PDF')
            pdf.close()
            return 0, '', ''

        self.expect(
            builder._execute(
                MATCH(lambda cmd: cmd.startswith('pdflatex ')))
            ).call(execute_mock)

        self.replay()
        self.assertTrue(builder.config.remove_build_directory)

        builder.add_file('mystyle.sty', 'LaTeX sty file content')

        data = builder.build_zip('LaTeX Code')
        self.assertTrue(hasattr(data, 'read'))

        zipobj = ZipFile(data)
        filenames_in_zip = zipobj.namelist()

        self.assertIn('export.tex', filenames_in_zip)
        self.assertIn('export.pdf', filenames_in_zip)
        self.assertIn('mystyle.sty', filenames_in_zip)

        self.assertEqual('LaTeX Code', zipobj.read('export.tex'))
        self.assertEqual('LaTeX sty file content',
                         zipobj.read('mystyle.sty'))

        self.assertFalse(os.path.exists(builder.build_directory))

    def test_build_removes_directory_even_if_build_failed(self):
        builder = self.mocker.patch(getUtility(IBuilderFactory)())

        self.expect(builder._execute(ANY)).result((
                1, '', 'could not build pdf for some reason...'))

        self.replay()

        with self.assertRaises(PDFBuildFailed) as cm:
            builder.build('LaTeX')
        self.assertEqual(str(cm.exception),
                         'PDF missing.')

        self.assertFalse(os.path.exists(builder.build_directory))

    def test_build_zip_removes_directory_even_if_build_failed(self):
        builder = self.mocker.patch(getUtility(IBuilderFactory)())

        self.expect(builder._execute(ANY)).result((
                1, '', 'could not build pdf for some reason...'))

        self.replay()

        builder.build_zip('LaTeX')

        self.assertFalse(os.path.exists(builder.build_directory))

    def test_execute_runs_command_in_build_directory(self):
        builder = getUtility(IBuilderFactory)()

        file_ = open(os.path.join(builder.build_directory, 'foo.txt'), 'w+')
        file_.write('bar')
        file_.close()

        self.assertEqual(builder._execute('ls .'), (0, 'foo.txt\n', ''))
        self.assertEqual(builder._execute('cat foo.txt'), (0, 'bar', ''))
        self.assertEqual(builder._execute('cat baz'),
                         (1, '', 'cat: baz: No such file or directory\n'))

    def test_build_pdf_reruns_pdflatex_if_needed(self):
        builder = self.mocker.patch(getUtility(IBuilderFactory)())
        aux_path = os.path.join(self.builddir, 'export.aux')
        pdf_path = os.path.join(self.builddir, 'export.pdf')

        self._reruns__executed_call_counter = 0

        def exec_mock(cmd):
            self._reruns__executed_call_counter += 1
            if self._reruns__executed_call_counter == 1:
                aux = open(aux_path, 'w+')
                aux.write('first run')
                aux.close()
                pdf = open(pdf_path, 'w+')
                pdf.write('the pdf')
                pdf.close()
                return (0, 'some log\nRerun to get it better\ndone', '')

            elif self._reruns__executed_call_counter == 2:
                aux = open(aux_path, 'wa')
                aux.write('second run')
                aux.close()
                return (0, 'some log', '')

            elif self._reruns__executed_call_counter == 3:
                # no change in aux
                return (0, 'some log', '')

        self.expect(builder._execute(ANY)).call(exec_mock).count(3)

        self.replay()

        builder._build_pdf(u'The latex')

    def test_maximum_reruns(self):
        builder = getUtility(IBuilderFactory)()
        rerun_limit = builder._rerun_limit
        builder = self.mocker.patch(builder)

        aux_path = os.path.join(self.builddir, 'export.aux')

        def exec_mock(cmd):
            aux = open(aux_path, 'a+')
            aux.write('another run')
            aux.close()
            return (0, 'some log', '')

        self.expect(builder._execute(ANY)).call(exec_mock).count(rerun_limit)

        self.replay()

        with self.assertRaises(PDFBuildFailed) as cm:
            builder._build_pdf('The latex')
        self.assertEqual(str(cm.exception),
                         'Maximum pdf build limit reached.')

    def test_build_pdf_executes_makeindex(self):
        builder = self.mocker.patch(getUtility(IBuilderFactory)())
        aux_path = os.path.join(self.builddir, 'export.aux')
        pdf_path = os.path.join(self.builddir, 'export.pdf')

        def pdflatex_call_mock(cmd):
            with open(aux_path, 'w+') as aux:
                aux.write('first run')
            with open(pdf_path, 'w+') as pdf:
                pdf.write('the pdf')
            return (0, 'the log', '')

        # Runs 2 times by default, does not rerun because _makeindex
        # returns False (non rerun required)
        self.expect(builder._execute(ANY)).call(pdflatex_call_mock).count(2)
        self.expect(builder._makeindex()).result(False)

        self.replay()

        builder._build_pdf(u'LaTeX')

    def test_build_pdf_reruns_when_makeindex_requires_rerun(self):
        builder = self.mocker.patch(getUtility(IBuilderFactory)())
        aux_path = os.path.join(self.builddir, 'export.aux')
        pdf_path = os.path.join(self.builddir, 'export.pdf')

        def pdflatex_call_mock(cmd):
            with open(aux_path, 'w+') as aux:
                aux.write('first run')
            with open(pdf_path, 'w+') as pdf:
                pdf.write('the pdf')
            return (0, 'the log', '')

        # Runs 3 times: 2 by default + once because _makeindex requires
        # an additional run by returning True
        self.expect(builder._execute(ANY)).call(pdflatex_call_mock).count(3)
        self.expect(builder._makeindex()).result(True)

        self.replay()

        builder._build_pdf(u'LaTeX')

    def test_makeindex_does_nothing_and_returns_False_without_idx_file(self):
        builder = getUtility(IBuilderFactory)()
        self.assertEquals(False, builder._makeindex())

    def test_makeindex_calls_executable_and_returns_True_with_idx_file(self):
        builder = self.mocker.patch(getUtility(IBuilderFactory)())
        idx_path = os.path.join(self.builddir, 'export.idx')
        with open(idx_path, 'w+') as idx:
            idx.write('\indexentry{Test}{2}')

        (self.expect(builder._execute('makeindex -g -s umlaut.ist export'))
         .result((0, 'stdout', 'stderr')))

        self.replay()
        self.assertEquals(True, builder._makeindex())

    def test_cleanup(self):
        builder = getUtility(IBuilderFactory)()
        self.assertTrue(os.path.exists(builder.build_directory))
        builder.cleanup()
        self.assertFalse(os.path.exists(builder.build_directory))

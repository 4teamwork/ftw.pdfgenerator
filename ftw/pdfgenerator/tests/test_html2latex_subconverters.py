from ftw.pdfgenerator.html2latex.converter import HTML2LatexConverter
from ftw.pdfgenerator.html2latex.subconverter import SubConverter
from ftw.pdfgenerator.interfaces import ISubConverter
from ftw.testing import MockTestCase
from zope.interface.verify import verifyClass
import re


class TestBaseSubConverter(MockTestCase):

    def test_implements_interface(self):
        self.assertTrue(ISubConverter.implementedBy(SubConverter))
        verifyClass(ISubConverter, SubConverter)

    def test_init(self):
        converter = object()
        match = object()
        html = object()

        obj = SubConverter(converter=converter, match=match, html=html)
        self.assertEqual(obj.converter, converter)
        self.assertEqual(obj.match, match)
        self.assertEqual(obj.fullhtml, html)

    def test_call_not_implemented(self):
        converter = match = html = object()
        obj = SubConverter(converter, match, html)

        with self.assertRaises(NotImplementedError):
            obj()

    def test_get_html_returns_matched_html(self):
        html = 'one three five'
        match = re.search('t[\w]*', html)

        obj = SubConverter(object(), match, html)
        self.assertEqual(obj.get_html(), 'three')

    def test_replace_and_lock_passed_to_converter(self):
        html = 'one three five'
        match = re.search('t[\w]*', html)
        converter = self.mocker.mock()

        self.expect(converter.replace_and_lock(4, 9, 'latex code'))

        self.replay()

        obj = SubConverter(converter, match, html)
        obj.replace_and_lock('latex code')

    def test_replace_passed_to_converter(self):
        html = 'one three five'
        match = re.search('t[\w]*', html)
        converter = self.mocker.mock()

        self.expect(converter.replace(4, 9, 'latex code'))

        self.replay()

        obj = SubConverter(converter, match, html)
        obj.replace('latex code')

    def test_get_context(self):
        context = self.mocker.mock()
        self.expect(context.found())

        class MySubConverter(SubConverter):
            pattern = 'y'

            def __call__(self):
                self.get_context().found()

        self.replay()

        converter = HTML2LatexConverter(
            context=context,
            request=object(),
            layout=object())

        converter.convert('xyz', custom_subconverters=[MySubConverter])

    def test_get_layout(self):
        layout = self.mocker.mock()
        self.expect(layout.found())

        class MySubConverter(SubConverter):
            pattern = 'y'

            def __call__(self):
                self.get_layout().found()

        self.replay()

        converter = HTML2LatexConverter(
            context=object(),
            request=object(),
            layout=layout)

        converter.convert('xyz', custom_subconverters=[MySubConverter])

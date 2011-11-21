# pylint: disable=C0321
# C0321: More than one statement on a single line

from ftw.pdfgenerator import utils
from unittest2 import TestCase


class TestBaseclasses(TestCase):

    def test_single_object_class(self):
        class A(object): pass
        self.assertEqual(utils.baseclasses(A), [A, object])

    def test_multiple_object_classes(self):
        class A(object): pass
        class B(A): pass
        class C(B): pass
        class C2(B): pass

        self.assertEqual(utils.baseclasses(C), [C, B, A, object])
        self.assertEqual(utils.baseclasses(C2), [C2, B, A, object])

    def test_multi_inherited(self):
        class A(object): pass
        class B(object): pass
        class AB(A, B): pass
        class C(object): pass
        class ABC(AB, C): pass

        self.assertEqual(utils.baseclasses(ABC),
                         [ABC, AB, A, object, B, C])

    def test_same_baseclass(self):
        class A(object): pass
        class A1(A): pass
        class A2(A): pass
        class A12(A1, A2): pass
        class B(object): pass
        class A12B(A12, B): pass

        self.assertEqual(utils.baseclasses(A12B),
                         [A12B, A12, A1, A, object, A2, B])


class TestEntities(TestCase):

    def test_decode_htmlentites(self):
        self.assertEqual(utils.decode_htmlentities('&quot;X&gt;Y&quot;'),
                         u'"X>Y"')
        self.assertEqual(utils.decode_htmlentities('m&#38;m'),
                         u'm&m')
        self.assertEqual(utils.decode_htmlentities('a&foo;b'),
                         u'a&foo;b')

    def test_html2xmlentities(self):
        self.assertEqual(utils.html2xmlentities('m&amp;m'),
                         'm&#38;m')
        self.assertEqual(utils.html2xmlentities('a&foo;b'),
                         'a&foo;b')

    def test_xml2htmlentities(self):
        self.assertEqual(utils.xml2htmlentities('m&#38;m'),
                         'm&amp;m')
        self.assertEqual(utils.xml2htmlentities('a&#9999;b'),
                         'a&#9999;b')



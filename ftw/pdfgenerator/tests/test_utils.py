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

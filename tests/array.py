import unittest

from tivars.models import *
from tivars.types import *


class ListTests(unittest.TestCase):
    def test_real_list(self):
        test_real_list = TIRealList.open("tests/data/var/RealList.8xl")
        self.assertEqual(test_real_list, TIList.open("tests/data/var/RealList.8xl"))

        test_list = [TIReal("-1.0"), TIReal("2.0"), TIReal("999")]

        self.assertEqual(test_real_list.name, "Z")
        self.assertEqual(test_real_list.length, 3)
        self.assertEqual(test_real_list.list(), test_list)
        self.assertEqual(list(iter(test_real_list)), test_list)
        self.assertEqual(str(test_real_list), string := "[-1, 2, 999]")
        self.assertEqual(f"{test_real_list:t}", "{~1,2,999}")

        test_real_list.clear()
        test_real_list.load_list(test_list)
        self.assertEqual(list(test_real_list), test_list)

        test_real_list.clear()
        test_real_list.load_string(string)
        self.assertEqual(list(test_real_list), test_list)


    def test_complex_list(self):
        test_comp_list = TIComplexList.open("tests/data/var/ComplexList.8xl")
        self.assertEqual(test_comp_list, TIList.open("tests/data/var/ComplexList.8xl"))

        test_list = [TIComplex(1 + 1j), TIComplex("-3 + 2i"), TIComplex(4 + 0j)]

        self.assertEqual(test_comp_list.name, "I")
        self.assertEqual(test_comp_list.length, 3)
        self.assertEqual(test_comp_list.get_min_os(), TI_83.OS())
        self.assertEqual(test_comp_list.list(), test_list)
        self.assertEqual(list(iter(test_comp_list)), test_list)
        self.assertEqual(str(test_comp_list), string := "[1 + i, -3 + 2i, 4]")
        self.assertEqual(f"{test_comp_list:t}", "{1+[i],~3+2[i],4}")

        test_comp_list.clear()
        test_comp_list.load_list(test_list)
        self.assertEqual(list(test_comp_list), test_list)

        test_comp_list.clear()
        test_comp_list.load_string(string)
        self.assertEqual(list(test_comp_list), test_list)


class MatrixTests(unittest.TestCase):
    def test_matrix(self):
        test_matrix = TIMatrix.open("tests/data/var/Matrix_3x3_standard.8xm")

        test_array = [[TIReal(0.5), TIReal(-1.0), TIReal("2.6457513110646")],
                      [TIReal("2.7386127875258"), TIReal("0.5"), TIReal("3.1415926535898")],
                      [TIReal("1"), TIReal(99999999), TIReal(0)]]

        self.assertEqual(test_matrix.name, "[A]")
        self.assertEqual(test_matrix.height, 3)
        self.assertEqual(test_matrix.width, 3)
        self.assertEqual(test_matrix.matrix(), test_array)
        self.assertEqual(list(iter(test_matrix)), [entry for row in test_array for entry in row])

        self.assertEqual(str(test_matrix), string := "[[0.5, -1, 2.6457513110646],"
                                           " [2.7386127875258, 0.5, 3.1415926535898],"
                                           " [1, 99999999, 0]]")
        self.assertEqual(f"{test_matrix:t}", "[[0.5,~1,2.6457513110646]"
                                             "[2.7386127875258,0.5,3.1415926535898]"
                                             "[1,99999999,0]]")

        test_matrix.clear()
        test_matrix.load_matrix(test_array)
        self.assertEqual(test_matrix.matrix(), test_array)

        test_matrix.clear()
        test_matrix.load_string(string)
        self.assertEqual(test_matrix.matrix(), test_array)

    def test_exact_matrix(self):
        test_matrix = TIMatrix.open("tests/data/var/Matrix_2x2_exact.8xm")

        test_array = [[TIRealPi("3π"), TIRealRadical("3√10")],
                      [TIRealFraction("1/2"), TIRealRadical("(4√5 + 2√3) / 7")]]

        self.assertEqual(test_matrix.name, "[B]")
        self.assertEqual(test_matrix.height, 2)
        self.assertEqual(test_matrix.width, 2)
        self.assertEqual(test_matrix.get_min_os(), TI_83PCE.OS())
        self.assertEqual(test_matrix.matrix(), test_array)
        self.assertEqual(list(iter(test_matrix)), [entry for row in test_array for entry in row])

        self.assertEqual(str(test_matrix), string := "[[3π, 3√10], [1/2, (4√5+2√3)/7]]")
        self.assertEqual(f"{test_matrix:t}", "[[3π,3sqrt(10)][1n/d2,(4sqrt(5)+2sqrt(3))n/d7]]")

        test_matrix.clear()
        test_matrix.load_string(string)
        self.assertEqual(test_matrix.matrix(), test_array)

import unittest

from decimal import Decimal

from tivars.types import *


class RealTests(unittest.TestCase):
    def real_float_test(self, real_type, filename, name, sign, exponent, mantissa, string, dec):
        test_num = real_type.open(f"tests/data/var/{filename}.8xn")

        self.assertEqual(test_num.name, name)
        self.assertEqual(test_num.sign, sign)
        self.assertEqual(test_num.exponent, exponent)
        self.assertEqual(test_num.mantissa, mantissa)

        self.assertEqual(str(test_num), string)
        self.assertEqual(f"{test_num:.2f}", f"{dec:.2f}")
        self.assertEqual(test_num.decimal(), dec)

        test_num.clear()
        test_num.load_string(string)
        self.assertEqual(test_num.string(), string)

        with open(f"tests/data/var/{filename}.8xn", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_num.bytes(), file.read()[:-2])

    def test_real_number(self):
        self.real_float_test(TIReal, "Real", "A", -1, 129, 42133700000000, "-42.1337",
                             Decimal("-42.1337"))

    def test_real_pi(self):
        self.real_float_test(TIRealPi, "Exact_RealPi", "C", 1, 129, 30000000000000, "30π",
                             Decimal("94.247779607694"))

    def test_real_pi_frac(self):
        self.real_float_test(TIRealPiFraction, "Exact_RealPiFrac", "D", 1, 127, 28571428571429, "2π/7",
                             Decimal("0.89759790102567"))

    def test_real_radical(self):
        test_radical = TIRealRadical.open("tests/data/var/Exact_RealRadical.8xn")

        self.assertEqual(test_radical.sign_type, 0)
        self.assertEqual(test_radical.left_scalar, 41)
        self.assertEqual(test_radical.left_radicand, 789)
        self.assertEqual(test_radical.right_scalar, 14)
        self.assertEqual(test_radical.right_radicand, 654)
        self.assertEqual(test_radical.denominator, 259)

        self.assertEqual(str(test_radical), "(41√789+14√654)/259")

        test_alternate = TIRealRadical("(4√3-2√1)/2")
        self.assertEqual(f"{test_alternate}", "(4√3-2)/2")
        self.assertEqual(f"{test_alternate:#}", "(4√3-2√1)/2")


class ComplexTests(unittest.TestCase):
    def complex_float_test(self, comp_type, filename, name, real_sign, real_exponent, real_mantissa,
                           imag_sign, imag_exponent, imag_mantissa, string, comp):

        test_num = comp_type.open(f"tests/data/var/{filename}.8xc")

        self.assertEqual(test_num.real.sign, real_sign)
        self.assertEqual(test_num.real.exponent, real_exponent)
        self.assertEqual(test_num.real.mantissa, real_mantissa)

        self.assertEqual(test_num.imag.sign, imag_sign)
        self.assertEqual(test_num.imag.exponent, imag_exponent)
        self.assertEqual(test_num.imag.mantissa, imag_mantissa)

        self.assertEqual(str(test_num), string)
        self.assertEqual(f"{test_num:.2f}", f"{comp:.2f}")

        self.assertEqual(test_num.name, name)
        test_components = comp_type(name=name)
        test_components.real, test_components.imag = test_num.real, test_num.imag
        self.assertEqual(test_num, test_components)
        self.assertEqual(test_components.components()[0], test_num.real)
        self.assertEqual(test_components.components()[1], test_num.imag)

        test_num.clear()
        test_num.load_string(string)
        self.assertEqual(test_num.string(), string)

        with open(f"tests/data/var/{filename}.8xc", 'rb') as file:
            file.seek(55)
            self.assertEqual(test_num.bytes(), file.read()[:-2])

    def test_complex_number(self):
        self.complex_float_test(TIComplex, "Complex", "C", -1, 128, 50000000000000,
                                1, 128, 20000000000000, "-5 + 2i", -5 + 2j)

    def test_complex_frac(self):
        self.complex_float_test(TIComplexFraction, "Exact_ComplexFrac", "E", 1, 127, 20000000000000,
                                -1, 127, 40000000000000, "1/5 - 2i/5", 0.2 - 0.4j)

    def test_complex_pi(self):
        self.complex_float_test(TIComplexPi, "Exact_ComplexPi", "H", 1, 127, 20000000000000,
                                -1, 128, 30000000000000, "1/5 - 3πi", 0.2 - 9.42j)

    def test_complex_pi_frac(self):
        self.complex_float_test(TIComplexPiFraction, "Exact_ComplexPiFrac", "A", 1, 128, 0,
                                1, 127, 28571428571429, "2πi/7", 0.90j)

    def test_coercion(self):
        test_num = TIComplexFraction("1 + 3/5i")
        self.assertEqual(test_num.real_type, TIReal)
        self.assertEqual(test_num.imag_type, TIRealFraction)
        self.assertEqual(str(test_num), "1 + 3i/5")

        test_num.imag = TIReal("0.6")
        self.assertEqual(test_num.real_type, TIReal)
        self.assertEqual(test_num.imag_type, TIReal)
        self.assertEqual(str(test_num), "1 + 0.6i")
        self.assertEqual(type(test_num), TIComplex)

import unittest

from decimal import Decimal, ROUND_DOWN, ROUND_HALF_EVEN, localcontext

from tivars.types import *


def round_to_mantissa(string: str) -> Decimal:
    """
    Independent reference for the value a mantissa should hold

    The decimal literal is parsed exactly, then rounded to the 14 digits of a mantissa.
    """

    exact = Decimal(string)

    with localcontext() as ctx:
        ctx.prec = 14
        ctx.rounding = ROUND_HALF_EVEN

        return +exact


class RoundingTests(unittest.TestCase):
    def test_mantissa_is_rounded(self):
        # Truncating instead of rounding loses the last digit and never carries
        for string, mantissa, exponent in [("1.23456789012344", 12345678901234, 0x80),
                                           ("1.23456789012346", 12345678901235, 0x80),
                                           ("1.4999999999999949", 15000000000000, 0x80),
                                           ("9.99999999999996", 10000000000000, 0x81),
                                           ("0.99999999999999999", 10000000000000, 0x80),
                                           ("9999999999999999", 10000000000000, 0x90),
                                           ("0.000123456789012349", 12345678901235, 0x7C)]:
            with self.subTest(string=string):
                real = TIReal(string)

                self.assertEqual(real.mantissa, mantissa)
                self.assertEqual(real.exponent, exponent)
                self.assertEqual(real.decimal(), round_to_mantissa(string))

    def test_sign_is_preserved_by_carry(self):
        self.assertEqual(TIReal("-9.99999999999996").decimal(), Decimal("-10"))
        self.assertEqual(TIReal("-9.99999999999996").sign, -1)

    def test_ties_round_half_even(self):
        # Matches the rounding TIRealFraction already uses to reach 14 digits
        self.assertEqual(TIReal("1.23456789012345").mantissa, 12345678901234)
        self.assertEqual(TIReal("1.23456789012335").mantissa, 12345678901234)

    def test_ignores_ambient_decimal_context(self):
        # The stored value must not depend on the caller's decimal context
        with localcontext() as ctx:
            ctx.prec = 5
            ctx.rounding = ROUND_DOWN

            self.assertEqual(TIReal("1.23456789012346").mantissa, 12345678901235)
            self.assertEqual(TIRealFraction("2/3").mantissa, 66666666666667)

    def test_leading_zeros(self):
        # Leading zeros must not shift the mantissa; "0000000000000000009" once loaded as 0
        for string in ["0009.5", "0010.5", "00.5", "0000000000000000009", "000.000123"]:
            with self.subTest(string=string):
                self.assertEqual(TIReal(string).decimal(), round_to_mantissa(string))

    def test_float_input(self):
        # A float's exact binary expansion runs well past 14 digits
        for number in [0.7, 2.675, 8.7]:
            with self.subTest(number=number):
                self.assertEqual(TIReal(number).float(), number)

        # A float needing more than 14 digits still lands on the nearest mantissa
        self.assertEqual(TIReal(1 / 3).decimal(), round_to_mantissa(str(Decimal(1 / 3))))

    def test_every_real_type_rounds(self):
        # All of these funnel into TIReal.load_string
        self.assertEqual(TIUndefinedReal("9.99999999999996").mantissa, 10000000000000)
        self.assertEqual(TIRealPi("9.99999999999996π").mantissa, 10000000000000)
        self.assertEqual(TIComplex("9.99999999999996").real.mantissa, 10000000000000)
        self.assertEqual(TIComplex("9.99999999999996i").imag.mantissa, 10000000000000)
        self.assertEqual(TIRealList("{9.99999999999996}").list()[0].mantissa, 10000000000000)
        self.assertEqual(TIMatrix("[[9.99999999999996]]").matrix()[0][0].mantissa, 10000000000000)

    def test_format_keeps_all_digits(self):
        # A mantissa holds 14 significant digits, not 14 decimal places
        self.assertEqual(str(TIReal("1e-20")), "0.00000000000000000001")
        self.assertEqual(str(TIReal("0.00012345678901235")), "0.00012345678901235")
        self.assertEqual(str(TIReal("1.5e20")), "150000000000000000000")
        self.assertEqual(str(TIRealPi("1e-20π")), "0.00000000000000000001π")

    def test_string_round_trip(self):
        for mantissa in [10000000000000, 12345678901235, 99999999999999]:
            for exponent in [0x01, 0x6C, 0x80, 0x94, 0xFE]:
                with self.subTest(mantissa=mantissa, exponent=exponent):
                    real = TIReal()
                    real.mantissa, real.exponent, real.sign_bit = mantissa, exponent, 1

                    self.assertEqual(TIReal(str(real)).calc_data, real.calc_data)


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

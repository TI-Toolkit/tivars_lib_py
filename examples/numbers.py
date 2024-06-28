from decimal import Decimal
from fractions import Fraction

from tivars import *


# Reading numbers
my_real = TIReal.open("EXAMPLE.8xn")

my_float = my_real.float()        # Convert to a float (can lose precision)
my_float = float(my_real)         # You can use the builtin type constructors too
my_string = my_real.string()      # Convert to a string (won't lose precision)
my_decimal = my_real.decimal()    # Convert to a Decimal (won't lose precision)


my_real_radical = TIRealRadical.open("EXAMPLE.8xn")

my_float = my_real_radical.float()        # Convert to a float (WILL lose precision)
my_string = my_real_radical.string()      # Convert to a string (won't lose precision)
my_decimal = my_real_radical.decimal()    # Convert to a Decimal (WILL lose precision)


my_real_fraction = TIRealFraction("EXAMPLE.8xn")

my_float = my_real_fraction.float()          # Convert to a float (can lose precision)
my_string = my_real_fraction.string()        # Convert to a string (won't lose precision)
my_fraction = my_real_fraction.fraction()    # Convert to a Fraction (won't lose precision)


# Writing numbers
my_real = TIReal(3.14)                     # Load a float value
my_complex = TIComplex(2 + 3j)             # Load a complex value
pi = TIReal("3.1415926535")                # Load a string
e = TIReal(Decimal("2.718281828"))         # Load a Decimal object

sqrt2 = TIRealRadical(1.414213562)               # Errors; radical types DO NOT support loading floats
sqrt2 = TIRealRadical("sqrt(2)")                 # Use a string instead
five_fourths = TIRealFraction(1.25)              # Fraction types DO support floats
five_fourths = TIRealFraction(Fraction(5, 4))    # As well as Fraction objects


three = TIReal(1) + TIReal(2)                          # Errors; operations on TIReal objects are NOT supported
float_three = TIReal(1).float() + TIReal(2).float()    # Instead, convert to a numeric type first...
three = TIReal(float_three)                             # ...then load back into a TIReal

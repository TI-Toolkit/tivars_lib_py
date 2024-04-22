from tivars import *


# Detokenize a program
my_program = TIProgram.open("EXAMPLE.8xp")
code = my_program.string()


# Unprotect a program
my_program = TIProtectedProgram.open("EXAMPLE.8xp")
my_program.unprotect()


# Turn a real number into a float
my_real = TIReal.open("EXAMPLE.8xn")
value = my_real.float()


# Put real numbers into a list
my_reals = TIReal(1), TIReal(2), TIReal(3)
lst = TIRealList(my_reals)


# Ungroup a group
my_group = TIGroup.open("EXAMPLE.8xg")
entries = my_group.ungroup()


# Put inaccessible tokens into a string
my_string = TIString("αβγ")


# Convert an exact number into a real number
my_exact = TIRealRadical.open("EXAMPLE.8xn")
real = TIReal(my_exact.float())


# Open a flash app
my_flash = TIApp.open("EXAMPLE.8ek")

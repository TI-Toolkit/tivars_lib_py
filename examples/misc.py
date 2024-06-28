from tivars import *


# Put real numbers into a list
my_reals = TIReal(1), TIReal(2), TIReal(3)
lst = TIRealList(my_reals)


# Ungroup a group
my_group = TIGroup.open("EXAMPLE.8xg")
entries = my_group.ungroup()


# Put inaccessible tokens into a string
my_string = TIString("αβγ")


# Add an equation to a GDB
my_gdb = TIFuncGDB()
my_gdb.Y1 = TIEquation("sin(X)")


# Open a flash app
my_flash = TIApp.open("EXAMPLE.8ek")

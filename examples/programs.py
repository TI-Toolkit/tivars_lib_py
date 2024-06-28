from tivars import *


# 8xp -> Plaintext
my_program = TIProgram.open("EXAMPLE.8xp")

code = my_program.string()              # The program's code
os_version = my_program.get_min_os()    # The minimum OS version supported by the program
my_program.unprotect()                  # Unprotect the program (no-op if it already is)


# Plaintext -> 8xp
my_program = TIProgram()

my_program.load_string("EXAMPLE CODE")                  # Tokenize some code
my_program.load_string("EXAMPLE CODE", model=TI_84P)    # Errors if the code isn't supported by the TI-84+
my_program.protect()                                    # Protect the program

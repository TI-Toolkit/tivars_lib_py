from tivars import *


# Tokenization

my_program = TIProgram("HELLO", TI_84pce)

with open("HELLO.8xp", 'rb') as file:
    my_program.load(file)
    file.seek(0)

    assert my_program.dump() == file.read()

    my_program.loads(program := "Disp \"HELLO WORLD!\"")
    file.seek(0)

    assert my_program.dump() == file.read()
    assert my_program.dumps() == program

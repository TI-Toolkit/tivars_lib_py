from tivars.models import TI_84pce
from tivars.vars import TIProgram

if __name__ == "__main__":
    my_program = TIProgram("HELLO", TI_84pce)
    my_program.loads("Disp \"HELLO WORLD!\"")

    with open("HELLO.8xp", 'wb+') as file:
        file.write(my_program.dump())

    print(my_program.dumps())

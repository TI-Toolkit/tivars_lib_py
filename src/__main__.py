from src.models import TI_84pce
from src.vars.types import TIProgram

if __name__ == "__main__":
    my_program = TIProgram(TI_84pce)
    my_program.loads("Disp \"Hello World!\"")

    with open("HELLO.8xp", 'wb+') as file:
        file.write(my_program.dump())

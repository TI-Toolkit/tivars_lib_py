from src.models import TI_84pce
from src.vars import TIVar

if __name__ == "__main__":
    with open("HELLO.8xp", 'rb') as file:
        my_program = TIVar.infer(file, model=TI_84pce)

    my_program.loads("Disp \"Hello World\"")

    with open("HELLO.8xp", 'wb+') as file:
        file.write(my_program.dump())

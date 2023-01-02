from tivars.models import TI_84pce
from tivars.vars import TIProgram

if __name__ == "__main__":
    my_program = TIProgram("HELLO", TI_84pce)
    my_program.loads("Disp \"HELLO WORLD!\"")
    my_program.save()
    print(my_program.dumps())

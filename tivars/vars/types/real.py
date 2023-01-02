from tivars.models import *
from ..var import TIVar


class TIReal(TIVar):
    extensions = {
        TI_82: "82n",
        TI_83: "83n",
        TI_82a: "8xn",
        TI_83p: "8xn",
        TI_84p: "8xn",
        TI_84pcse: "8xn",
        TI_84pce: "8xn",
        TI_83pce: "8xn"
    }

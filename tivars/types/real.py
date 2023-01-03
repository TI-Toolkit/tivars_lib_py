from tivars.models import *
from ..var import TIVar


class TIReal(TIVar):
    extensions = {
        TI_82: "82n",
        TI_83: "83n",
        TI_82a: "8xn",
        TI_82p: "8xn",
        TI_83p: "8xn",
        TI_84p: "8xn",
        TI_84t: "8xn",
        TI_84pcse: "8xn",
        TI_84pce: "8xn",
        TI_84pcet: "8xn",
        TI_84pcetpy: "8xn",
        TI_84pcepy: "8xn",
        TI_83pce: "8xn",
        TI_83pceep: "8xn",
        TI_82aep: "8xn"
    }

    type_id = b'\x00'

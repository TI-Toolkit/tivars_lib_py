from tivars.models import *
from ..data import *
from ..var import SizedEntry


class TIAppVar(SizedEntry, register=True):
    flash_only = True

    extensions = {
        None: "8xv",
        TI_82: "",
        TI_83: "",
        TI_82A: "8xv",
        TI_82P: "8xv",
        TI_83P: "8xv",
        TI_84P: "8xv",
        TI_84T: "8xv",
        TI_84PCSE: "8xv",
        TI_84PCE: "8xv",
        TI_84PCEPY: "8xv",
        TI_83PCE: "8xv",
        TI_83PCEEP: "8xv",
        TI_82AEP: "8xv"
    }

    _type_id = 0x15


__all__ = ["TIAppVar"]

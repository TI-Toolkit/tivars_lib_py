from tivars.models import *
from ..var import TIEntry


class TIRealFraction(TIEntry):
    extensions = {
        None: "8xn",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "8xn",
        TI_83P: "8xn",
        TI_84P: "8xn",
        TI_84T: "8xn",
        TI_84PCSE: "8xn",
        TI_84PCE: "8xn",
        TI_84PCEPY: "8xn",
        TI_83PCE: "8xn",
        TI_83PCEEP: "8xn",
        TI_82AEP: "8xn"
    }

    _type_id = b'\x18'


__all__ = ["TIRealFraction"]

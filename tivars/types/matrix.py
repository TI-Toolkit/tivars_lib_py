from tivars.models import *
from ..var import TIEntry


class TIMatrix(TIEntry):
    extensions = {
        None: "8xm",
        TI_82: "82m",
        TI_83: "83m",
        TI_82A: "8xm",
        TI_82P: "8xm",
        TI_83P: "8xm",
        TI_84P: "8xm",
        TI_84T: "8xm",
        TI_84PCSE: "8xm",
        TI_84PCE: "8xm",
        TI_84PCEPY: "8xm",
        TI_83PCE: "8xm",
        TI_83PCEEP: "8xm",
        TI_82AEP: "8xm"
    }

    type_id = b'\x02'


__all__ = ["TIMatrix"]

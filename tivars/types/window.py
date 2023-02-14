from tivars.models import *
from ..var import TIVar


class TIWindowSettings(TIVar):
    extensions = {
        None: "8xw",
        TI_82: "82w",
        TI_83: "83w",
        TI_82A: "8xw",
        TI_82P: "8xw",
        TI_83P: "8xw",
        TI_84P: "8xw",
        TI_84T: "8xw",
        TI_84PCSE: "8xw",
        TI_84PCE: "8xw",
        TI_84PCEPY: "8xw",
        TI_83PCE: "8xw",
        TI_83PCEEP: "8xw",
        TI_82AEP: "8xw"
    }

    type_id = b'\x0F'


class TIRecallWindow(TIVar):
    extensions = {
        None: "8xz",
        TI_82: "82z",
        TI_83: "83z",
        TI_82A: "8xz",
        TI_82P: "8xz",
        TI_83P: "8xz",
        TI_84P: "8xz",
        TI_84T: "8xz",
        TI_84PCSE: "8xz",
        TI_84PCE: "8xz",
        TI_84PCEPY: "8xz",
        TI_83PCE: "8xz",
        TI_83PCEEP: "8xz",
        TI_82AEP: "8xz"
    }

    type_id = b'\x10'


__all__ = ["TIWindowSettings", "TIRecallWindow"]
from tivars.models import *
from ..flash import TIFlashHeader


class TIOS(TIFlashHeader, register=True):
    extensions = {
        None: "8eu",
        TI_82A: "82u",
        TI_84PCSE: "8cu",
        TI_84PCE: "8eu",
        TI_83PCE: "8pu",
        TI_82AEP: "8yu"
    }

    _type_id = 0x23


class TIApp(TIFlashHeader, register=True):
    extensions = {
        None: "8ek",
        TI_83P: "8xk",
        TI_84PCSE: "8ck",
        TI_84PCE: "8ek"
    }

    _type_id = 0x24


class TICertificate(TIFlashHeader, register=True):
    extensions = {
        None: "8eq",
        TI_83P: "8xq",
        TI_84PCSE: "8cq",
        TI_84PCE: "8eq"
    }

    _type_id = 0x25


__all__ = ["TIOS", "TIApp", "TICertificate"]
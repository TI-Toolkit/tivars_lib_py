from tivars.models import *
from ..var import TIEntry


class TIExactComplexFraction(TIEntry):
    flash_only = True

    extensions = {
        None: "8xc",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "",
        TI_83P: "",
        TI_84P: "",
        TI_84T: "",
        TI_84PCSE: "",
        TI_84PCE: "",
        TI_84PCEPY: "8xc",
        TI_83PCE: "8xc",
        TI_83PCEEP: "8xc",
        TI_82AEP: "8xc"
    }

    _type_id = b'\x1B'


class TIExactRealRadical(TIEntry):
    flash_only = True

    extensions = {
        None: "8xn",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "",
        TI_83P: "",
        TI_84P: "",
        TI_84T: "",
        TI_84PCSE: "",
        TI_84PCE: "",
        TI_84PCEPY: "8xn",
        TI_83PCE: "8xn",
        TI_83PCEEP: "8xn",
        TI_82AEP: "8xn"
    }

    _type_id = b'\x1C'


class TIExactComplexRadical(TIEntry):
    flash_only = True

    extensions = {
        None: "8xc",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "",
        TI_83P: "",
        TI_84P: "",
        TI_84T: "",
        TI_84PCSE: "",
        TI_84PCE: "",
        TI_84PCEPY: "8xc",
        TI_83PCE: "8xc",
        TI_83PCEEP: "8xc",
        TI_82AEP: "8xc"
    }

    _type_id = b'\x1D'


class TIExactComplexPi(TIEntry):
    flash_only = True

    extensions = {
        None: "8xc",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "",
        TI_83P: "",
        TI_84P: "",
        TI_84T: "",
        TI_84PCSE: "",
        TI_84PCE: "",
        TI_84PCEPY: "8xc",
        TI_83PCE: "8xc",
        TI_83PCEEP: "8xc",
        TI_82AEP: "8xc"
    }

    _type_id = b'\x1E'


class TIExactComplexPiFraction(TIEntry):
    flash_only = True

    extensions = {
        None: "8xc",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "",
        TI_83P: "",
        TI_84P: "",
        TI_84T: "",
        TI_84PCSE: "",
        TI_84PCE: "",
        TI_84PCEPY: "8xc",
        TI_83PCE: "8xc",
        TI_83PCEEP: "8xc",
        TI_82AEP: "8xc"
    }

    _type_id = b'\x1F'


class TIExactRealPi(TIEntry):
    flash_only = True

    extensions = {
        None: "8xn",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "",
        TI_83P: "",
        TI_84P: "",
        TI_84T: "",
        TI_84PCSE: "",
        TI_84PCE: "",
        TI_84PCEPY: "8xn",
        TI_83PCE: "8xn",
        TI_83PCEEP: "8xn",
        TI_82AEP: "8xn"
    }

    _type_id = b'\x20'


class TIExactRealPiFraction(TIEntry):
    flash_only = True

    extensions = {
        None: "8xn",
        TI_82: "",
        TI_83: "",
        TI_82A: "",
        TI_82P: "",
        TI_83P: "",
        TI_84P: "",
        TI_84T: "",
        TI_84PCSE: "",
        TI_84PCE: "",
        TI_84PCEPY: "8xn",
        TI_83PCE: "8xn",
        TI_83PCEEP: "8xn",
        TI_82AEP: "8xn"
    }

    _type_id = b'\x21'


__all__ = ["TIExactComplexFraction", "TIExactRealRadical", "TIExactComplexRadical",
           "TIExactComplexPi", "TIExactComplexPiFraction", "TIExactRealPi", "TIExactRealPiFraction"]

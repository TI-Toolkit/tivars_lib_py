from tivars.models import *
from ..var import SizedEntry


class TIAppVar(SizedEntry, register=True):
    """
    Parser for application variables (appvars)

    An appvar is a sized block of data, to be interpreted by the corresponding app as desired.
    Certain common formats, such as compiled Python modules, are denoted by a header at the start of the data block.
    """

    flash_only = True

    extensions = {
        None: "8xv",
        TI_83P: "8xv",
    }

    _type_id = 0x15

    def get_min_os(self, data: bytes = None) -> OsVersion:
        return TI_83P.OS()


__all__ = ["TIAppVar"]

"""
Appvars
"""


from tivars.data import *
from tivars.models import *
from tivars.var import SizedEntry


class TIAppVar(SizedEntry, register=True):
    """
    Parser for application variables (appvars)

    An appvar is a sized block of data, to be interpreted by the corresponding app as desired.
    Certain common formats, such as compiled Python modules, are denoted by a header at the start of the data block.
    """

    flash_only = True

    extension = "8xv"

    _type_id = 0x15

    def __init__(self, init=None, *,
                 name: str = "UNNAMED",
                 version: int = None, archived: bool = True,
                 data: bytes = None):

        super().__init__(init, name=name, version=version, archived=archived, data=data)

    @datamethod
    @classmethod
    def get_min_os(cls, data: bytes) -> OsVersion:
        return TI_83P.OS()


__all__ = ["TIAppVar"]

from tivars.models import *
from ..data import *
from ..var import TIEntry
from .numeric import TIReal


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

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the dimensions of the matrix, followed by sequential real variable data sections
        """

    @View(data, Integer)[0:1]
    def width(self) -> int:
        """
        The number of columns in the matrix

        Cannot exceed 255, though TI-OS imposes a limit of 99
        """

    @View(data, Integer)[1:2]
    def width(self) -> int:
        """
        The number of columns in the matrix

        Cannot exceed 255, though TI-OS imposes a limit of 99
        """


__all__ = ["TIMatrix"]

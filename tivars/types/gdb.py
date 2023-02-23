from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry
from .numeric import TIReal


class TIGDB(TIEntry):
    extensions = {
        None: "8xd",
        TI_82: "82d",
        TI_83: "83d",
        TI_82A: "8xd",
        TI_82P: "8xd",
        TI_83P: "8xd",
        TI_84P: "8xd",
        TI_84T: "8xd",
        TI_84PCSE: "8xd",
        TI_84PCE: "8xd",
        TI_84PCEPY: "8xd",
        TI_83PCE: "8xd",
        TI_83PCEEP: "8xd",
        TI_82AEP: "8xd"
    }

    _type_id = b'\x08'

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Integer)[0:2]
    def length(self):
        """
        Two less than the length of the GDB
        """

    @property
    def mode(self) -> str:
        """
        The mode for the GDB

        One of Func, Param, Polar, or Seq
        """
        match self.data[3]:
            case 0x10: return 'Func'
            case 0x40: return 'Param'
            case 0x20: return 'Polar'
            case 0x80: return 'Seq'

    @View(data, Bytes)[4:5]
    def mode_flags(self) -> int:
        """
        The flags for the mode settings
        """

    @View(data, Bytes)[5:6]
    def extended_mode_flags(self) -> int:
        """
        The flags for the extended mode settings
        """

    @View(data, TIReal)[7:16]
    def Xmin(self) -> TIReal:
        """
        Xmin: the smallest or leftmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[16:25]
    def Xmax(self) -> TIReal:
        """
        Xmax: the largest or rightmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[25:34]
    def Xscl(self) -> TIReal:
        """
        Xscl: the separation between ticks on the horizontal axis
        """

    @View(data, TIReal)[34:43]
    def Ymin(self) -> TIReal:
        """
        Ymin: the smallest or bottommost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[43:52]
    def Ymax(self) -> TIReal:
        """
        Ymax: the largest or topmost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[52:61]
    def Yscl(self) -> TIReal:
        """
        Yscl: the separation between ticks on the vertical axis
        """

    def coerce(self):
        match self.data[3]:
            case 0x10: self.__class__ = TIFuncGDB


class TIFuncGDB:
    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Integer)[70:71]
    def Y1Style(self) -> int:
        """
        The style byte for Y1
        """

    @View(data, Integer)[71:72]
    def Y2Style(self) -> int:
        """
        The style byte for Y2
        """

    @View(data, Integer)[72:73]
    def Y3Style(self) -> int:
        """
        The style byte for Y3
        """

    @View(data, Integer)[73:74]
    def Y4Style(self) -> int:
        """
        The style byte for Y4
        """

    @View(data, Integer)[74:75]
    def Y5Style(self) -> int:
        """
        The style byte for Y5
        """

    @View(data, Integer)[75:76]
    def Y6Style(self) -> int:
        """
        The style byte for Y6
        """

    @View(data, Integer)[76:77]
    def Y7Style(self) -> int:
        """
        The style byte for Y7
        """

    @View(data, Integer)[77:78]
    def Y8Style(self) -> int:
        """
        The style byte for Y8
        """

    @View(data, Integer)[78:79]
    def Y9Style(self) -> int:
        """
        The style byte for Y9
        """

    @View(data, Integer)[79:80]
    def Y0Style(self) -> int:
        """
        The style byte for Y0
        """


__all__ = ["TIGDB", "TIFuncGDB"]

import io

from warnings import warn

from tivars.models import *
from ..flags import *
from ..data import *
from ..var import TIEntry
from .numeric import TIReal
from .tokenized import TIEquation


class GraphMode(Flags):
    Dot = {0: 1}
    Connected = {0: 0}
    Simul = {1: 1}
    Sequential = {1: 0}
    GridOn = {2: 1}
    GridOff = {2: 0}
    PolarGC = {3: 1}
    RectGC = {3: 0}
    CoordOff = {4: 0}
    CoordOn = {4: 1}
    AxesOff = {5: 1}
    AxesOn = {5: 0}
    LabelOn = {6: 1}
    LabelOff = {6: 0}

    ExprOff = {0: 1}
    ExprOn = {0: 0}

    Time = {0: 0, 2: 0, 3: 0, 4: 0}
    Web = {0: 1, 2: 0, 3: 0, 4: 0}
    uv = {0: 0, 2: 1, 3: 0, 4: 0}
    vw = {0: 0, 2: 0, 3: 1, 4: 0}
    uw = {0: 0, 2: 0, 3: 0, 4: 1}


class GraphStyle(Converter):
    SOLID_LINE = 0
    THICK_LINE = 1
    SHADE_ABOVE = 2
    SHADE_BELOW = 3
    TRACE = 4
    ANIMATE = 5
    DOTTED_LINE = 6

    @classmethod
    def get(cls, data: bytes, instance: 'TIGDB') -> int:
        return data[0]

    @classmethod
    def set(cls, value: int, instance: 'TIGDB') -> bytes:
        if value not in STYLES:
            warn(f"{value} is not a recognized style.",
                 BytesWarning)

        return bytes([value])


STYLES = [GraphStyle.SOLID_LINE, GraphStyle.THICK_LINE, GraphStyle.SHADE_BELOW, GraphStyle.SHADE_BELOW,
          GraphStyle.TRACE, GraphStyle.ANIMATE, GraphStyle.DOTTED_LINE]


def equations_from_data(data: bytes, num_equations: int) -> tuple[TIEquation, ...]:
    data = io.BytesIO(data)
    equations = ()
    for i in range(num_equations):
        data.seek(1, 1)
        equation = TIEquation()
        equation.load_data_section(data)
        equations += (equation,)

    return equations


def IndexedEquation(index: int):
    index -= 1

    class Equation(Converter):
        _T = TIEquation

        @classmethod
        def get(cls, data: bytes, instance: 'TIGDB') -> _T:
            return equations_from_data(data, instance.num_equations)[index]

        @classmethod
        def set(cls, value: _T, instance: 'TIGDB') -> bytes:
            equations = list(instance.equations)
            equations[index] = value

            return b''.join(equation.data for equation in equations)

    return Equation


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

    num_equations = 0
    num_parameters = 0

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

    @View(data, GraphMode)[4:5]
    def mode_flags(self) -> GraphMode:
        """
        The flags for the mode settings
        """

    @View(data, GraphMode)[6:7]
    def extended_mode_flags(self) -> GraphMode:
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

    @property
    def equations(self) -> tuple[TIEquation, ...]:
        """
        The GDB's stored graph equations
        """

        offset = 61 + TIReal.data.width * self.num_parameters + self.num_equations
        return equations_from_data(self.data[offset:][:self.num_equations], self.num_equations)

    @property
    def styles(self) -> tuple[bytes, ...]:
        """
        The GDB's stored graph styles
        """

        return *self.data[61 + TIReal.data.width * self.num_parameters:][:self.num_equations],

    def coerce(self):
        match self.data[3]:
            case 0x10: self.__class__ = TIFuncGDB


class TIFuncGDB(TIGDB):
    num_equations = 10
    num_parameters = 1

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, TIReal)[61:70]
    def Xres(self, value: TIReal) -> TIReal:
        """
        Xres: the pixel separation of points in a function plot

        Must be an integer between 1 and 8
        """

        if int(value) != float(value) or not 1 <= int(value) <= 8:
            warn(f"Expected an integer in [1, 8] for Xres, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, GraphStyle)[70:71]
    def Y1Style(self) -> bytes:
        """
        The style byte for Y1
        """

    @View(data, GraphStyle)[71:72]
    def Y2Style(self) -> bytes:
        """
        The style byte for Y2
        """

    @View(data, GraphStyle)[72:73]
    def Y3Style(self) -> bytes:
        """
        The style byte for Y3
        """

    @View(data, GraphStyle)[73:74]
    def Y4Style(self) -> bytes:
        """
        The style byte for Y4
        """

    @View(data, GraphStyle)[74:75]
    def Y5Style(self) -> bytes:
        """
        The style byte for Y5
        """

    @View(data, GraphStyle)[75:76]
    def Y6Style(self) -> bytes:
        """
        The style byte for Y6
        """

    @View(data, GraphStyle)[76:77]
    def Y7Style(self) -> bytes:
        """
        The style byte for Y7
        """

    @View(data, GraphStyle)[77:78]
    def Y8Style(self) -> bytes:
        """
        The style byte for Y8
        """

    @View(data, GraphStyle)[78:79]
    def Y9Style(self) -> bytes:
        """
        The style byte for Y9
        """

    @View(data, GraphStyle)[79:80]
    def Y0Style(self) -> bytes:
        """
        The style byte for Y0
        """

    @View(data, Bytes)[70:80]
    def style_data(self) -> bytes:
        """
        The styles of the equations stored in the GDB
        """

    @View(data, IndexedEquation(1))[80:]
    def Y1(self) -> TIEquation:
        """
        Y1: The first equation in function mode
        """

    @View(data, IndexedEquation(2))[80:]
    def Y2(self) -> TIEquation:
        """
        Y2: The second equation in function mode
        """

    @View(data, IndexedEquation(3))[80:]
    def Y3(self) -> TIEquation:
        """
        Y3: The third equation in function mode
        """

    @View(data, IndexedEquation(4))[80:]
    def Y4(self) -> TIEquation:
        """
        Y4: The fourth equation in function mode
        """

    @View(data, IndexedEquation(5))[80:]
    def Y5(self) -> TIEquation:
        """
        Y5: The fifth equation in function mode
        """

    @View(data, IndexedEquation(6))[80:]
    def Y6(self) -> TIEquation:
        """
        Y6: The sixth equation in function mode
        """

    @View(data, IndexedEquation(7))[80:]
    def Y7(self) -> TIEquation:
        """
        Y7: The seventh equation in function mode
        """

    @View(data, IndexedEquation(8))[80:]
    def Y8(self) -> TIEquation:
        """
        Y8: The eight equation in function mode
        """

    @View(data, IndexedEquation(9))[80:]
    def Y9(self) -> TIEquation:
        """
        Y9: The ninth equation in function mode
        """

    @View(data, IndexedEquation(10))[80:]
    def Y0(self) -> TIEquation:
        """
        Y0: The tenth equation in function mode
        """

    @View(data, Bytes)[80:]
    def equation_data(self) -> bytes:
        """
        The equations stored in the GDB as a contiguous buffer of equation data sections
        """


__all__ = ["TIGDB", "TIFuncGDB", "GraphMode", "GraphStyle"]

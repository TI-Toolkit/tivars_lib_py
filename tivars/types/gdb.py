import io

from warnings import warn

from tivars.models import *
from ..flags import *
from ..data import *
from ..var import TIEntry, TIEntryRaw
from .numeric import TIReal
from .tokenized import TIEquation


class GraphMode(Flags):
    Dot = {0: 1}
    Connected = {0: 0}
    Simul = {1: 1}
    Sequential = {1: 0}
    GridOn = {2: 1, 7: 0}
    GridOff = {2: 0, 7: 0}
    GridLine = {2: 1, 7: 1}
    GridDot = {2: 1, 7: 0}
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
    SEQ_n = {1: 0, 2: 0}
    SEQ_n_1 = {1: 1, 2: 0}
    SEQ_n_2 = {1: 0, 2: 1}

    Time = {0: 0, 2: 0, 3: 0, 4: 0}
    Web = {0: 1, 2: 0, 3: 0, 4: 0}
    uv = {0: 0, 2: 1, 3: 0, 4: 0}
    vw = {0: 0, 2: 0, 3: 1, 4: 0}
    uw = {0: 0, 2: 0, 3: 0, 4: 1}

    DetectAsymptotesOn = {0: 1}
    DetectAsymptotesOff = {0: 0}


class GraphStyle(Enum):
    SOLID_LINE = b'\x00'
    THICK_LINE = b'\x01'
    SHADE_ABOVE = b'\x02'
    SHADE_BELOW = b'\x03'
    TRACE = b'\x04'
    ANIMATE = b'\x05'
    DOTTED_LINE = b'\x06'

    _all = [SOLID_LINE, THICK_LINE, SHADE_BELOW, SHADE_BELOW, TRACE, ANIMATE, DOTTED_LINE]
    STYLES = _all


class GraphColor(Enum):
    MONO = b'\x00'
    BLUE = b'\x01'
    RED = b'\x02'
    BLACK = b'\x03'
    MAGENTA = b'\x04'
    GREEN = b'\x05'
    ORANGE = b'\x06'
    BROWN = b'\x07'
    NAVY = b'\x08'
    LTBLUE = 'b\x09'
    YELLOW = b'\x0A'
    WHITE = b'\x0B'
    LTGRAY = b'\x0C'
    MEDGRAY = b'\x0D'
    GRAY = b'\x0E'
    DARKGRAY = b'\x0F'

    _all = [MONO, BLUE, RED, BLACK, MAGENTA, GREEN, ORANGE, BROWN, NAVY,
            LTBLUE, YELLOW, WHITE, LTGRAY, MEDGRAY, GRAY, DARKGRAY]
    COLORS = _all[1:]


class LineStyle(Enum):
    THICK = b'\x00'
    THIN = b'\x01'
    DOT_THICK = b'\x02'
    DOT_THIN = b'\x03'

    _all = [THICK, THIN, DOT_THIN, DOT_THICK]
    STYLES = _all


class BorderColor(Enum):
    GRAY = b'\x01'
    TEAL = b'\x02'
    LTBLUE = b'\x03'
    WHITE = b'\x04'

    _all = [GRAY, TEAL, LTBLUE, WHITE]
    COLORS = _all


class EquationFlags(Flags):
    SELECTED = {5: 1}
    DESELECTED = {5: 0}
    USED_FOR_GRAPH = {6: 1}
    UNUSED_FOR_GRAPH = {6: 0}
    LINK_TRANSFER_SET = {7: 1}
    LINK_TRANSFER_CLEAR = {7: 0}


class TIPlottedEquationRaw(TIEntryRaw):
    __slots__ = "meta_length", "_data_length", "type_id", "name", "version", "archived", "_data_length", \
                "flags", "__style", "__color", "data"


class TIPlottedEquation(TIEquation):
    _raw_class = TIPlottedEquationRaw

    @Section(1, EquationFlags)
    def flags(self) -> EquationFlags:
        """
        The flags for the equation

        Whether the equation is selected, used for graphing, or is participating in a link transfer
        """

    @Section(1, GraphStyle)
    def style(self) -> bytes:
        """
        The style of the equation
        """

    @Section(1, GraphColor)
    def color(self) -> bytes:
        """
        The color of the equation
        """

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the tokens and their total size
        """

    @View(data, Integer)[0:2]
    def length(self) -> int:
        """
        The total size of the tokens
        """

    def load_data_section(self, data: io.BytesIO):
        self.raw.flags = data.read(1)
        data_length = int.from_bytes(data.read(2), 'little')
        self.raw.data = int.to_bytes(data_length, 2, 'little') + data.read(data_length)

    def load_equation(self, equation: TIEquation):
        self.raw.data = equation.data

    def equation(self) -> TIEquation:
        return TIEquation(self.bytes()[:-self.data_length - 1] + self.bytes()[-self.data_length:])


def equations_from_data(data: bytes, gdb: 'TIMonoGDB') -> tuple[tuple[TIPlottedEquation, ...], bytes]:
    data = io.BytesIO(data[61 + TIReal.data.width * gdb.num_parameters:])
    equations = tuple(TIPlottedEquation() for _ in range(gdb.num_equations))

    for i in range(gdb.num_styles):
        style = data.read(1)
        for j in range(r := gdb.num_equations // gdb.num_styles):
            equations[r * i + j].style = style

    for i in range(gdb.num_equations):
        equations[i].load_data_section(data)

    if rest := data.read():
        data = io.BytesIO(rest)
        data.seek(3, 1)

        for i in range(gdb.num_styles):
            color = data.read(1)
            for j in range(r := gdb.num_equations // gdb.num_styles):
                equations[r * i + j].color = color

    return equations, rest


def IndexedEquation(index: int):
    index -= 1

    class Equation(Converter):
        _T = TIPlottedEquation

        @classmethod
        def get(cls, data: bytes, instance: 'TIMonoGDB') -> _T:
            return equations_from_data(data, instance)[0][index]

        @classmethod
        def set(cls, value: _T, instance: 'TIMonoGDB') -> bytes:
            equations = list(instance.equations)
            equations[index] = value

            data = b''
            for i in range(instance.num_styles):
                data += equations[i].style
                i += instance.num_equations // instance.num_styles

            data += b''.join(equation.bytes() for equation in equations)

            if equations_from_data(instance.data, instance)[1]:
                for i in range(instance.num_styles):
                    data += equations[i].color
                    i += instance.num_equations // instance.num_styles

            return instance.raw.data[:instance.offset] + data

    return Equation


class TIMonoGDB(TIEntry):
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
    mode_byte = 0x00

    num_equations = 0
    num_parameters = 0
    num_styles = 0

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
    def mode_id(self) -> int:
        """
        The mode ID for the GDB

        One of 0x10, 0x20, 0x40, or 0x80
        """
        return self.data[3]

    @property
    def mode(self) -> str:
        """
        The mode for the GDB

        One of Func, Param, Polar, or Seq
        """
        match self.mode_id:
            case 0x10: return 'Func'
            case 0x40: return 'Param'
            case 0x20: return 'Polar'
            case 0x80: return 'Seq'

            case _: warn(f"Graphing mode byte 0x{self.mode_id:x} not recognized.",
                         BytesWarning)

    @View(data, GraphMode)[4:5]
    def mode_flags(self) -> GraphMode:
        """
        The flags for the mode settings

        Dot/Connected, Simul/Sequential, GridOn/Line/Dot/Off, PolarGC/RectGC, CoordOn/Off, AxesOff/On, and LabelOn/Off
        """

    @View(data, GraphMode)[6:7]
    def extended_mode_flags(self) -> GraphMode:
        """
        The flags for the extended mode settings

        ExprOn/Off and sequence plot offsets for sequence mode
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
    def offset(self) -> int:
        return 61 + TIReal.data.width * self.num_parameters

    @property
    def equations(self) -> tuple[TIPlottedEquation, ...]:
        """
        The GDB's stored graph equations
        """

        return equations_from_data(self.data, self)[0]

    @property
    def styles(self) -> tuple[int, ...]:
        """
        The GDB's stored graph styles
        """

        return *map(lambda b: bytes([b]), self.data[self.offset:][:self.num_styles]),

    def coerce(self):
        if equations_from_data(self.data, self)[1]:
            self.__class__ = TIGDB
            self.coerce()
        else:
            match self.mode_id:
                case 0x10: self.__class__ = TIMonoFuncGDB
                case 0x40: self.__class__ = TIMonoParamGDB
                case 0x20: self.__class__ = TIMonoPolarGDB
                case 0x80: self.__class__ = TIMonoSeqGDB

                case _:
                    warn(f"Graphing mode byte 0x{self.mode_id:x} not recognized.",
                         BytesWarning)


class TIGDB(TIMonoGDB):
    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, GraphColor)[-5:-4]
    def grid_color(self) -> bytes:
        """
        The color of the grid
        """

    @View(data, GraphColor)[-4:-3]
    def axes_color(self) -> bytes:
        """
        The color of the axes
        """

    @View(data, LineStyle)[-3:-2]
    def line_style(self) -> bytes:
        """
        The line style for all plotted equations
        """

    @View(data, BorderColor)[-2:-1]
    def border_color(self) -> bytes:
        """
        The color of the graph border
        """

    @View(data, GraphMode)[-1:]
    def color_mode_flags(self) -> GraphMode:
        """
        The flags for extended color mode settings

        Only DetectAsymptotesOn/Off is stored here
        """

    def coerce(self):
        match self.mode_id:
            case 0x10: self.__class__ = TIFuncGDB
            case 0x40: self.__class__ = TIParamGDB
            case 0x20: self.__class__ = TIPolarGDB
            case 0x80: self.__class__ = TISeqGDB

            case _:
                warn(f"Graphing mode byte 0x{self.mode_id:x} not recognized.",
                     BytesWarning)


class TIMonoFuncGDB(TIMonoGDB):
    mode_byte = 0x10

    num_equations = 10
    num_parameters = 1
    num_styles = 10

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

    @View(data, IndexedEquation(1))
    def Y1(self) -> TIPlottedEquation:
        """
        Y1: The first equation in function mode
        """

    @View(data, IndexedEquation(2))
    def Y2(self) -> TIPlottedEquation:
        """
        Y2: The second equation in function mode
        """

    @View(data, IndexedEquation(3))
    def Y3(self) -> TIPlottedEquation:
        """
        Y3: The third equation in function mode
        """

    @View(data, IndexedEquation(4))
    def Y4(self) -> TIPlottedEquation:
        """
        Y4: The fourth equation in function mode
        """

    @View(data, IndexedEquation(5))
    def Y5(self) -> TIPlottedEquation:
        """
        Y5: The fifth equation in function mode
        """

    @View(data, IndexedEquation(6))
    def Y6(self) -> TIPlottedEquation:
        """
        Y6: The sixth equation in function mode
        """

    @View(data, IndexedEquation(7))
    def Y7(self) -> TIPlottedEquation:
        """
        Y7: The seventh equation in function mode
        """

    @View(data, IndexedEquation(8))
    def Y8(self) -> TIPlottedEquation:
        """
        Y8: The eight equation in function mode
        """

    @View(data, IndexedEquation(9))
    def Y9(self) -> TIPlottedEquation:
        """
        Y9: The ninth equation in function mode
        """

    @View(data, IndexedEquation(10))
    def Y0(self) -> TIPlottedEquation:
        """
        Y0: The tenth equation in function mode
        """


class TIFuncGDB(TIGDB, TIMonoFuncGDB):
    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, String)[-18:-15]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """


class TIMonoParamGDB(TIMonoGDB):
    mode_byte = 0x40

    num_equations = 12
    num_parameters = 3
    num_styles = 6

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, TIReal)[61:70]
    def Tmin(self) -> TIReal:
        """
        Tmin: the initial time
        """

    @View(data, TIReal)[70:79]
    def Tmax(self) -> TIReal:
        """
        Tmax: the final time
        """

    @View(data, TIReal)[79:88]
    def Tstep(self) -> TIReal:
        """
        Tstep: the time increment
        """

    @View(data, IndexedEquation(1))
    def X1T(self) -> TIPlottedEquation:
        """
        X1T: The first X-component in parametric mode
        """

    @View(data, IndexedEquation(2))
    def Y1T(self) -> TIPlottedEquation:
        """
        Y1T: The first Y-component in parametric mode
        """

    @View(data, IndexedEquation(3))
    def X2T(self) -> TIPlottedEquation:
        """
        X2T: The second X-component in parametric mode
        """

    @View(data, IndexedEquation(4))
    def Y2T(self) -> TIPlottedEquation:
        """
        Y2T: The second Y-component in parametric mode
        """

    @View(data, IndexedEquation(5))
    def X3T(self) -> TIPlottedEquation:
        """
        X3T: The third X-component in parametric mode
        """

    @View(data, IndexedEquation(6))
    def Y3T(self) -> TIPlottedEquation:
        """
        Y3T: The third Y-component in parametric mode
        """

    @View(data, IndexedEquation(7))
    def X4T(self) -> TIPlottedEquation:
        """
        X4T: The fourth X-component in parametric mode
        """

    @View(data, IndexedEquation(8))
    def Y4T(self) -> TIPlottedEquation:
        """
        Y4T: The fourth Y-component in parametric mode
        """

    @View(data, IndexedEquation(9))
    def X5T(self) -> TIPlottedEquation:
        """
        X5T: The fifth X-component in parametric mode
        """

    @View(data, IndexedEquation(10))
    def Y5T(self) -> TIPlottedEquation:
        """
        Y5T: The fifth Y-component in parametric mode
        """

    @View(data, IndexedEquation(11))
    def X6T(self) -> TIPlottedEquation:
        """
        X6T: The sixth X-component in parametric mode
        """

    @View(data, IndexedEquation(12))
    def Y6T(self) -> TIPlottedEquation:
        """
        Y6T: The sixth Y-component in parametric mode
        """


class TIParamGDB(TIGDB, TIMonoParamGDB):
    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, String)[-14:-11]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """


class TIMonoPolarGDB(TIMonoGDB):
    mode_byte = 0x20

    num_equations = 6
    num_parameters = 3
    num_styles = 6

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, TIReal)[61:70]
    def Thetamin(self) -> TIReal:
        """
        Thetamin: the initial angle
        """

    @View(data, TIReal)[70:79]
    def Thetamax(self) -> TIReal:
        """
        Thetamax: the final angle
        """

    @View(data, TIReal)[79:88]
    def Thetastep(self) -> TIReal:
        """
        Thetastep: the angle increment
        """

    @View(data, IndexedEquation(1))
    def r1(self) -> TIPlottedEquation:
        """
        r1: The first equation in polar mode
        """

    @View(data, IndexedEquation(2))
    def r2(self) -> TIPlottedEquation:
        """
        r1: The second equation in polar mode
        """

    @View(data, IndexedEquation(3))
    def r3(self) -> TIPlottedEquation:
        """
        r3: The third equation in polar mode
        """

    @View(data, IndexedEquation(4))
    def r4(self) -> TIPlottedEquation:
        """
        rr: The fourth equation in polar mode
        """

    @View(data, IndexedEquation(5))
    def r5(self) -> TIPlottedEquation:
        """
        r5: The fifth equation in polar mode
        """

    @View(data, IndexedEquation(6))
    def r6(self) -> TIPlottedEquation:
        """
        r6: The sixth equation in polar mode
        """


class TIPolarGDB(TIGDB, TIMonoPolarGDB):
    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, String)[-14:-11]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """


class TIMonoSeqGDB(TIMonoGDB):
    mode_byte = 0x80

    num_equations = 3
    num_parameters = 10
    num_styles = 3

    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, GraphMode)[5:6]
    def sequence_flags(self) -> GraphMode:
        """
        The flags for the sequence mode settings
        """

    @View(data, TIReal)[61:70]
    def PlotStart(self, value) -> TIReal:
        """
        PlotStart: the initial value of n for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for PlotStart, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[70:79]
    def nMax(self, value: TIReal) -> TIReal:
        """
        nMax: the final value of n

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for nMax, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[79:88]
    def unMin0(self) -> TIReal:
        """
        u(nMin): the initial value of u at nMin
        """

    @View(data, TIReal)[88:97]
    def vnMin0(self) -> TIReal:
        """
        v(nMin): the initial value of v at nMin
        """

    @View(data, TIReal)[97:106]
    def nMin(self, value: TIReal) -> TIReal:
        """
        nMin: the initial value of n for sequential equations

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for nMin, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[106:115]
    def unMin1(self) -> TIReal:
        """
        u(nMin + 1): the initial value of u at nMin + 1
        """

    @View(data, TIReal)[115:124]
    def vnMin1(self) -> TIReal:
        """
        v(nMin + 1): the initial value of v at nMin + 1
        """

    @View(data, TIReal)[124:133]
    def wnMin0(self) -> TIReal:
        """
        w(nMin): the initial value of w at nMin
        """

    @View(data, TIReal)[133:142]
    def PlotStep(self, value: TIReal) -> TIReal:
        """
        PlotStep: the n increment for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for PlotStep, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[142:151]
    def wnMin1(self) -> TIReal:
        """
        w(nMin + 1): the initial value of w at nMin + 1
        """

    @View(data, IndexedEquation(1))
    def u(self) -> TIPlottedEquation:
        """
        u: The first equation in sequence mode
        """

    @View(data, IndexedEquation(2))
    def v(self) -> TIPlottedEquation:
        """
        v: The second equation in sequence mode
        """

    @View(data, IndexedEquation(3))
    def w(self) -> TIPlottedEquation:
        """
        w: The third equation in sequence mode
        """


class TISeqGDB(TIGDB, TIMonoSeqGDB):
    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, String)[-11:-8]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """


__all__ = ["TIMonoGDB", "TIMonoFuncGDB", "TIMonoParamGDB", "TIMonoPolarGDB", "TIMonoSeqGDB",
           "TIGDB", "TIFuncGDB", "TIParamGDB", "TIPolarGDB", "TISeqGDB",
           "TIPlottedEquation", "GraphMode", "GraphStyle", "GraphColor", "LineStyle"]

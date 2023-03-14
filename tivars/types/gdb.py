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
    SOLID_LINE = 0
    THICK_LINE = 1
    SHADE_ABOVE = 2
    SHADE_BELOW = 3
    TRACE = 4
    ANIMATE = 5
    DOTTED_LINE = 6

    _all = [SOLID_LINE, THICK_LINE, SHADE_BELOW, SHADE_BELOW, TRACE, ANIMATE, DOTTED_LINE]
    STYLES = _all


class GraphColor(Enum):
    OFF = 0
    BLUE = 1
    RED = 2
    BLACK = 3
    MAGENTA = 4
    GREEN = 5
    ORANGE = 6
    BROWN = 7
    NAVY = 8
    LTBLUE = 9
    YELLOW = 10
    WHITE = 11
    LTGRAY = 12
    MEDGRAY = 13
    GRAY = 14
    DARKGRAY = 15

    _all = [OFF, BLUE, RED, BLACK, MAGENTA, GREEN, ORANGE, BROWN, NAVY,
            LTBLUE, YELLOW, WHITE, LTGRAY, MEDGRAY, GRAY, DARKGRAY]
    COLORS = _all[1:]


class LineStyle(Enum):
    THICK = 0
    THIN = 1
    DOT_THICK = 2
    DOT_THIN = 3

    _all = [THICK, THIN, DOT_THIN, DOT_THICK]
    STYLES = _all


class BorderColor(Enum):
    GRAY = 1
    TEAL = 2
    LTBLUE = 3
    WHITE = 4

    _all = [GRAY, TEAL, LTBLUE, WHITE]
    COLORS = _all


def equations_from_data(data: bytes, num_equations: int) -> tuple[tuple[TIEquation, ...], bytes]:
    data = io.BytesIO(data)
    equations = ()
    for i in range(num_equations):
        data.seek(1, 1)
        equation = TIEquation()
        equation.load_data_section(data)
        equations += (equation,)

    return equations, data.read()


def IndexedEquation(index: int):
    index -= 1

    class Equation(Converter):
        _T = TIEquation

        @classmethod
        def get(cls, data: bytes, instance: 'TIMonoGDB') -> _T:
            return equations_from_data(data, instance.num_equations)[0][index]

        @classmethod
        def set(cls, value: _T, instance: 'TIMonoGDB') -> bytes:
            equations = list(instance.equations)
            equations[index] = value

            return b''.join(equation.data for equation in equations)

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

        Only ExprOn/Off is stored here
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

        offset = 61 + TIReal.data.width * self.num_parameters + self.num_styles
        return equations_from_data(self.data[offset:], self.num_equations)[0]

    @property
    def styles(self) -> tuple[int, ...]:
        """
        The GDB's stored graph styles
        """

        return *self.data[61 + TIReal.data.width * self.num_parameters:][:self.num_styles],

    def coerce(self):
        offset = 61 + TIReal.data.width * self.num_parameters + self.num_styles

        if equations_from_data(self.data[offset:], self.num_equations)[1]:
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
    def grid_color(self) -> int:
        """
        The color of the grid
        """

    @View(data, GraphColor)[-4:-3]
    def axes_color(self) -> int:
        """
        The color of the axes
        """

    @View(data, LineStyle)[-3:-2]
    def line_style(self) -> int:
        """
        The line style for all plotted equations
        """

    @View(data, BorderColor)[-2:-1]
    def border_color(self) -> int:
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

    @View(data, GraphStyle)[70:71]
    def Y1Style(self) -> int:
        """
        The style byte for Y1
        """

    @View(data, GraphStyle)[71:72]
    def Y2Style(self) -> int:
        """
        The style byte for Y2
        """

    @View(data, GraphStyle)[72:73]
    def Y3Style(self) -> int:
        """
        The style byte for Y3
        """

    @View(data, GraphStyle)[73:74]
    def Y4Style(self) -> int:
        """
        The style byte for Y4
        """

    @View(data, GraphStyle)[74:75]
    def Y5Style(self) -> int:
        """
        The style byte for Y5
        """

    @View(data, GraphStyle)[75:76]
    def Y6Style(self) -> int:
        """
        The style byte for Y6
        """

    @View(data, GraphStyle)[76:77]
    def Y7Style(self) -> int:
        """
        The style byte for Y7
        """

    @View(data, GraphStyle)[77:78]
    def Y8Style(self) -> int:
        """
        The style byte for Y8
        """

    @View(data, GraphStyle)[78:79]
    def Y9Style(self) -> int:
        """
        The style byte for Y9
        """

    @View(data, GraphStyle)[79:80]
    def Y0Style(self) -> int:
        """
        The style byte for Y0
        """

    @View(data, Bytes)[70:80]
    def style_data(self) -> int:
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


class TIFuncGDB(TIGDB, TIMonoFuncGDB):
    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Bytes)[80:-18]
    def equation_data(self) -> bytes:
        """
        The equations stored in the GDB as a contiguous buffer of equation data sections
        """

    @View(data, String)[-18:-15]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """

    @View(data, GraphColor)[-15:-14]
    def Y1Color(self) -> int:
        """
        The color of Y1
        """

    @View(data, GraphColor)[-14:-13]
    def Y2Color(self) -> int:
        """
        The color of Y2
        """

    @View(data, GraphColor)[-13:-12]
    def Y3Color(self) -> int:
        """
        The color of Y3
        """

    @View(data, GraphColor)[-12:-11]
    def Y4Color(self) -> int:
        """
        The color of Y4
        """

    @View(data, GraphColor)[-11:-10]
    def Y5Color(self) -> int:
        """
        The color of Y5
        """

    @View(data, GraphColor)[-10:-9]
    def Y6Color(self) -> int:
        """
        The color of Y6
        """

    @View(data, GraphColor)[-9:-8]
    def Y7Color(self) -> int:
        """
        The color of Y7
        """

    @View(data, GraphColor)[-8:-7]
    def Y8Color(self) -> int:
        """
        The color of Y8
        """

    @View(data, GraphColor)[-7:-6]
    def Y9Color(self) -> int:
        """
        The color of Y9
        """

    @View(data, GraphColor)[-6:-5]
    def Y0Color(self) -> int:
        """
        The color of Y0
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

    @View(data, GraphStyle)[88:89]
    def T1Style(self) -> bytes:
        """
        The style byte for X1T/Y1T
        """

    @View(data, GraphStyle)[89:90]
    def T2Style(self) -> bytes:
        """
        The style byte for X2T/Y2T
        """

    @View(data, GraphStyle)[90:91]
    def T3Style(self) -> bytes:
        """
        The style byte for X3T/Y3T
        """

    @View(data, GraphStyle)[91:92]
    def T4Style(self) -> bytes:
        """
        The style byte for X4T/Y4T
        """

    @View(data, GraphStyle)[92:93]
    def T5Style(self) -> bytes:
        """
        The style byte for X5T/Y5T
        """

    @View(data, GraphStyle)[93:94]
    def T6Style(self) -> bytes:
        """
        The style byte for X6T/Y6T
        """

    @View(data, Bytes)[88:94]
    def style_data(self) -> bytes:
        """
        The styles of the equations stored in the GDB
        """

    @View(data, IndexedEquation(1))[94:]
    def X1T(self) -> TIEquation:
        """
        X1T: The first X-component in parametric mode
        """

    @View(data, IndexedEquation(2))[94:]
    def Y1T(self) -> TIEquation:
        """
        Y1T: The first Y-component in parametric mode
        """

    @View(data, IndexedEquation(3))[94:]
    def X2T(self) -> TIEquation:
        """
        X2T: The second X-component in parametric mode
        """

    @View(data, IndexedEquation(4))[94:]
    def Y2T(self) -> TIEquation:
        """
        Y2T: The second Y-component in parametric mode
        """

    @View(data, IndexedEquation(5))[94:]
    def X3T(self) -> TIEquation:
        """
        X3T: The third X-component in parametric mode
        """

    @View(data, IndexedEquation(6))[94:]
    def Y3T(self) -> TIEquation:
        """
        Y3T: The third Y-component in parametric mode
        """

    @View(data, IndexedEquation(7))[94:]
    def X4T(self) -> TIEquation:
        """
        X4T: The fourth X-component in parametric mode
        """

    @View(data, IndexedEquation(8))[94:]
    def Y4T(self) -> TIEquation:
        """
        Y4T: The fourth Y-component in parametric mode
        """

    @View(data, IndexedEquation(9))[94:]
    def X5T(self) -> TIEquation:
        """
        X5T: The fifth X-component in parametric mode
        """

    @View(data, IndexedEquation(10))[94:]
    def Y5T(self) -> TIEquation:
        """
        Y5T: The fifth Y-component in parametric mode
        """

    @View(data, IndexedEquation(11))[94:]
    def X6T(self) -> TIEquation:
        """
        X6T: The sixth X-component in parametric mode
        """

    @View(data, IndexedEquation(12))[94:]
    def Y6T(self) -> TIEquation:
        """
        Y6T: The sixth Y-component in parametric mode
        """

    @View(data, Bytes)[94:]
    def equation_data(self) -> bytes:
        """
        The equations stored in the GDB as a contiguous buffer of equation data sections
        """


class TIParamGDB(TIGDB, TIMonoParamGDB):
    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Bytes)[80:-14]
    def equation_data(self) -> bytes:
        """
        The equations stored in the GDB as a contiguous buffer of equation data sections
        """

    @View(data, String)[-14:-11]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """

    @View(data, GraphColor)[-11:-10]
    def T1Color(self) -> int:
        """
        The color of X1T/Y1T
        """

    @View(data, GraphColor)[-10:-9]
    def T2Color(self) -> int:
        """
        The color of X2T/Y2T
        """

    @View(data, GraphColor)[-9:-8]
    def T3Color(self) -> int:
        """
        The color of X3T/Y3T
        """

    @View(data, GraphColor)[-8:-7]
    def T4Color(self) -> int:
        """
        The color of X4T/Y4T
        """

    @View(data, GraphColor)[-7:-6]
    def T5Color(self) -> int:
        """
        The color of X5T/Y5T
        """

    @View(data, GraphColor)[-6:-5]
    def T6Color(self) -> int:
        """
        The color of X6T/Y6T
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

    @View(data, GraphStyle)[88:89]
    def r1Style(self) -> bytes:
        """
        The style byte for r1
        """

    @View(data, GraphStyle)[89:90]
    def r2Style(self) -> bytes:
        """
        The style byte for r2
        """

    @View(data, GraphStyle)[90:91]
    def r3Style(self) -> bytes:
        """
        The style byte for r3
        """

    @View(data, GraphStyle)[91:92]
    def r4Style(self) -> bytes:
        """
        The style byte for r4
        """

    @View(data, GraphStyle)[92:93]
    def r5Style(self) -> bytes:
        """
        The style byte for r5
        """

    @View(data, GraphStyle)[93:94]
    def r6Style(self) -> bytes:
        """
        The style byte for r6
        """

    @View(data, Bytes)[88:94]
    def style_data(self) -> bytes:
        """
        The styles of the equations stored in the GDB
        """

    @View(data, IndexedEquation(1))[94:]
    def r1(self) -> TIEquation:
        """
        r1: The first equation in polar mode
        """

    @View(data, IndexedEquation(2))[94:]
    def r2(self) -> TIEquation:
        """
        r1: The second equation in polar mode
        """

    @View(data, IndexedEquation(3))[94:]
    def r3(self) -> TIEquation:
        """
        r3: The third equation in polar mode
        """

    @View(data, IndexedEquation(4))[94:]
    def r4(self) -> TIEquation:
        """
        rr: The fourth equation in polar mode
        """

    @View(data, IndexedEquation(5))[94:]
    def r5(self) -> TIEquation:
        """
        r5: The fifth equation in polar mode
        """

    @View(data, IndexedEquation(6))[94:]
    def r6(self) -> TIEquation:
        """
        r6: The sixth equation in polar mode
        """

    @View(data, Bytes)[94:]
    def equation_data(self) -> bytes:
        """
        The equations stored in the GDB as a contiguous buffer of equation data sections
        """


class TIPolarGDB(TIGDB, TIMonoPolarGDB):
    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Bytes)[80:-14]
    def equation_data(self) -> bytes:
        """
        The equations stored in the GDB as a contiguous buffer of equation data sections
        """

    @View(data, String)[-14:-11]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """

    @View(data, GraphColor)[-11:-10]
    def r1Color(self) -> int:
        """
        The color of r1
        """

    @View(data, GraphColor)[-10:-9]
    def r2Color(self) -> int:
        """
        The color of r2
        """

    @View(data, GraphColor)[-9:-8]
    def r3Color(self) -> int:
        """
        The color of r3
        """

    @View(data, GraphColor)[-8:-7]
    def r4Color(self) -> int:
        """
        The color of r4
        """

    @View(data, GraphColor)[-7:-6]
    def r5Color(self) -> int:
        """
        The color of r5
        """

    @View(data, GraphColor)[-6:-5]
    def r6Color(self) -> int:
        """
        The color of r6
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

    @View(data, GraphStyle)[151:152]
    def uStyle(self) -> bytes:
        """
        The style byte for u
        """

    @View(data, GraphStyle)[152:153]
    def vStyle(self) -> bytes:
        """
        The style byte for v
        """

    @View(data, GraphStyle)[153:154]
    def wStyle(self) -> bytes:
        """
        The style byte for w
        """

    @View(data, Bytes)[151:154]
    def style_data(self) -> bytes:
        """
        The styles of the equations stored in the GDB
        """

    @View(data, IndexedEquation(1))[154:]
    def u(self) -> TIEquation:
        """
        u: The first equation in sequence mode
        """

    @View(data, IndexedEquation(2))[154:]
    def v(self) -> TIEquation:
        """
        v: The second equation in sequence mode
        """

    @View(data, IndexedEquation(3))[154:]
    def w(self) -> TIEquation:
        """
        w: The third equation in sequence mode
        """

    @View(data, Bytes)[154:]
    def equation_data(self) -> bytes:
        """
        The equations stored in the GDB as a contiguous buffer of equation data sections
        """


class TISeqGDB(TIGDB, TIMonoSeqGDB):
    @Section()
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the mode settings, graphscreen settings, graph styles, and graph equations
        """

    @View(data, Bytes)[80:-11]
    def equation_data(self) -> bytes:
        """
        The equations stored in the GDB as a contiguous buffer of equation data sections
        """

    @View(data, String)[-11:-8]
    def color_magic(self) -> str:
        """
        Magic to identify the GDB as color-oriented

        Always set to 84C
        """

    @View(data, GraphColor)[-8:-7]
    def uColor(self) -> int:
        """
        The color of u
        """

    @View(data, GraphColor)[-7:-6]
    def vColor(self) -> int:
        """
        The color of v
        """

    @View(data, GraphColor)[-6:-5]
    def wColor(self) -> int:
        """
        The color of w
        """


__all__ = ["TIMonoGDB",
           "TIMonoFuncGDB", "TIMonoParamGDB", "TIMonoPolarGDB", "TIMonoSeqGDB",
           "TIFuncGDB", "TIParamGDB", "TIPolarGDB", "TISeqGDB",
           "GraphMode", "GraphStyle", "GraphColor", "LineStyle"]

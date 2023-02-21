from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry
from .numeric import TIReal


class TIWindowSettings(TIEntry):
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

    _type_id = b'\x0F'

    def __init__(self, string: str = None, *,
                 for_flash: bool = True, name: str = "UNNAMED",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):

        super().__init__(string, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.raw.data[0:3] = b'\xD0\x00\x00'

    @Section(210)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the window parameter values
        """

    @View(data, TIReal)[3:12]
    def Xmin(self) -> TIReal:
        """
        Xmin: the smallest or leftmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[12:21]
    def Xmax(self) -> TIReal:
        """
        Xmax: the largest or rightmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[21:30]
    def Xscl(self) -> TIReal:
        """
        Xscl: the separation between ticks on the horizontal axis
        """

    @View(data, TIReal)[30:39]
    def Ymin(self) -> TIReal:
        """
        Ymin: the smallest or bottommost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[39:48]
    def Ymax(self) -> TIReal:
        """
        Ymax: the largest or topmost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[48:57]
    def Yscl(self) -> TIReal:
        """
        Yscl: the separation between ticks on the vertical axis
        """

    @View(data, TIReal)[57:66]
    def Thetamin(self) -> TIReal:
        """
        Θmin: the initial angle for polar plots
        """

    @View(data, TIReal)[66:75]
    def Thetamax(self) -> TIReal:
        """
        Θmax: the final angle for polar plots
        """

    @View(data, TIReal)[75:84]
    def Thetastep(self) -> TIReal:
        """
        Θstep: the angle increment for polar plots
        """

    @View(data, TIReal)[84:93]
    def Tmin(self) -> TIReal:
        """
        Tmin: the initial time for parametric plots
        """

    @View(data, TIReal)[93:102]
    def Tmax(self) -> TIReal:
        """
        Tmax: the final time for parametric plots
        """

    @View(data, TIReal)[102:111]
    def Tstep(self) -> TIReal:
        """
        Tstep: the time increment for parametric plots
        """

    @View(data, TIReal)[111:120]
    def PlotStart(self, value: TIReal) -> TIReal:
        """
        PlotStart: the initial value of n for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for PlotStart, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[120:129]
    def nMax(self, value: TIReal) -> TIReal:
        """
        nMax: the final value of n for sequential equations and plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for nMax, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[129:138]
    def unMin0(self) -> TIReal:
        """
        u(nMin): the initial value of u at nMin
        """

    @View(data, TIReal)[138:147]
    def vnMin0(self) -> TIReal:
        """
        v(nMin): the initial value of v at nMin
        """

    @View(data, TIReal)[147:156]
    def nMin(self, value: TIReal) -> TIReal:
        """
        nMin: the initial value of n for sequential equations

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for nMin, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[156:165]
    def unMin1(self) -> TIReal:
        """
        u(nMin + 1): the initial value of u at nMin + 1
        """

    @View(data, TIReal)[165:174]
    def vnMin1(self) -> TIReal:
        """
        v(nMin + 1): the initial value of v at nMin + 1
        """

    @View(data, TIReal)[174:183]
    def wnMin0(self) -> TIReal:
        """
        w(nMin): the initial value of w at nMin
        """

    @View(data, TIReal)[183:192]
    def PlotStep(self, value: TIReal) -> TIReal:
        """
        PlotStep: the n increment for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for PlotStep, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[192:201]
    def Xres(self, value: TIReal) -> TIReal:
        """
        Xres: the pixel separation of points in a function plot

        Must be an integer between 1 and 8
        """

        if int(value) != float(value) or not 1 <= int(value) <= 8:
            warn(f"Expected an integer in [1, 8] for Xres, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[201:210]
    def wnMin1(self) -> TIReal:
        """
        w(nMin + 1): the initial value of w at nMin + 1
        """


class TIRecallWindow(TIEntry):
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

    _type_id = b'\x10'

    def __init__(self, string: str = None, *,
                 for_flash: bool = True, name: str = "UNNAMED",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        super().__init__(string, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.raw.data[0:2] = b'\xCF\x00'

    @Section(209)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the window parameter values
        """

    @View(data, TIReal)[2:11]
    def Xmin(self) -> TIReal:
        """
        Xmin: the smallest or leftmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[11:20]
    def Xmax(self) -> TIReal:
        """
        Xmax: the largest or rightmost horizontal coordinate on the graphscreen
        """

    @View(data, TIReal)[20:29]
    def Xscl(self) -> TIReal:
        """
        Xscl: the separation between ticks on the horizontal axis
        """

    @View(data, TIReal)[29:38]
    def Ymin(self) -> TIReal:
        """
        Ymin: the smallest or bottommost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[38:47]
    def Ymax(self) -> TIReal:
        """
        Ymax: the largest or topmost vertical coordinate on the graphscreen
        """

    @View(data, TIReal)[47:56]
    def Yscl(self) -> TIReal:
        """
        Yscl: the separation between ticks on the vertical axis
        """

    @View(data, TIReal)[56:65]
    def Thetamin(self) -> TIReal:
        """
        Θmin: the initial angle for polar plots
        """

    @View(data, TIReal)[65:74]
    def Thetamax(self) -> TIReal:
        """
        Θmax: the final angle for polar plots
        """

    @View(data, TIReal)[74:83]
    def Thetastep(self) -> TIReal:
        """
        Θstep: the angle increment for polar plots
        """

    @View(data, TIReal)[83:92]
    def Tmin(self) -> TIReal:
        """
        Tmin: the initial time for parametric plots
        """

    @View(data, TIReal)[92:101]
    def Tmax(self) -> TIReal:
        """
        Tmax: the final time for parametric plots
        """

    @View(data, TIReal)[101:110]
    def Tstep(self) -> TIReal:
        """
        Tstep: the time increment for parametric plots
        """

    @View(data, TIReal)[110:119]
    def PlotStart(self, value: TIReal) -> TIReal:
        """
        PlotStart: the initial value of n for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for PlotStart, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[119:128]
    def nMax(self, value: TIReal) -> TIReal:
        """
        nMax: the final value of n for sequential equations and plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for nMax, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[128:137]
    def unMin0(self) -> TIReal:
        """
        u(nMin): the initial value of u at nMin
        """

    @View(data, TIReal)[137:146]
    def vnMin0(self) -> TIReal:
        """
        v(nMin): the initial value of v at nMin
        """

    @View(data, TIReal)[146:155]
    def nMin(self, value: TIReal) -> TIReal:
        """
        nMin: the initial value of n for sequential equations

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for nMin, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[155:164]
    def unMin1(self) -> TIReal:
        """
        u(nMin + 1): the initial value of u at nMin + 1
        """

    @View(data, TIReal)[164:173]
    def vnMin1(self) -> TIReal:
        """
        v(nMin + 1): the initial value of v at nMin + 1
        """

    @View(data, TIReal)[173:182]
    def wnMin0(self) -> TIReal:
        """
        w(nMin): the initial value of w at nMin
        """

    @View(data, TIReal)[182:191]
    def PlotStep(self, value: TIReal) -> TIReal:
        """
        PlotStep: the n increment for sequential plots

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for PlotStep, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[191:200]
    def Xres(self, value) -> TIReal:
        """
        Xres: the pixel separation of points in a function plot

        Must be an integer between 1 and 8
        """

        if int(value) != float(value) or not 1 <= int(value) <= 8:
            warn(f"Expected an integer in [1, 8] for Xres, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[200:209]
    def wnMin1(self) -> TIReal:
        """
        w(nMin + 1): the initial value of w at nMin + 1
        """


class TITableSettings(TIEntry):
    extensions = {
        None: "8xt",
        TI_82: "82t",
        TI_83: "83t",
        TI_82A: "8xt",
        TI_82P: "8xt",
        TI_83P: "8xt",
        TI_84P: "8xt",
        TI_84T: "8xt",
        TI_84PCSE: "8xt",
        TI_84PCE: "8xt",
        TI_84PCEPY: "8xt",
        TI_83PCE: "8xt",
        TI_83PCEEP: "8xt",
        TI_82AEP: "8xt"
    }

    _type_id = b'\x11'

    def __init__(self, string: str = None, *,
                 for_flash: bool = True, name: str = "UNNAMED",
                 version: bytes = None, archived: bool = None,
                 data: bytearray = None):
        super().__init__(string, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

        self.raw.data[0:2] = b'\x12\x00'

    @Section(20)
    def data(self) -> bytearray:
        """
        The data section of the entry

        Contains the table parameter values
        """

    @View(data, TIReal)[2:11]
    def TblMin(self, value) -> TIReal:
        """
        TblMin: the initial value for the table

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for TblMin, got {float(value)}.",
                 UserWarning)

        return value

    @View(data, TIReal)[11:20]
    def DeltaTbl(self, value) -> TIReal:
        """
        ΔTbl: the increment for the table

        Must be an integer
        """

        if int(value) != float(value):
            warn(f"Expected an integer for ΔTbl, got {float(value)}.",
                 UserWarning)

        return value


__all__ = ["TIWindowSettings", "TIRecallWindow", "TITableSettings"]

from ..flags import *


Bitsets = dict[int, int]


class TIModel:
    def __init__(self, name: str, flags: Bitsets, magic: str, product_id: bytes):
        self.name = name
        self.flags = TIFeature("000000000") | flags
        self.magic = magic
        self.product_id = product_id

    def __str__(self):
        return self.name


class TIFeature(Flags):
    DEFAULT = {0: 1}
    COMPLEX = {1: 1}
    FLASH = {2: 1}
    APPS = {3: 1}
    CLOCK = {4: 1}
    COLOR = {5: 1}
    EZ80 = {6: 1}
    EXACT_MATH = {7: 1}
    PYTHON = {8: 1}


flags82 = TIFeature.DEFAULT
flags83 = flags82 | TIFeature.COMPLEX
flags82a = flags83 | TIFeature.FLASH
flags83p = flags82a | TIFeature.APPS
flags84p = flags83p | TIFeature.CLOCK
flags84pcse = flags84p | TIFeature.COLOR
flags84pce = flags84pcse | TIFeature.EZ80
flags83pce = flags84pce | TIFeature.EXACT_MATH
flags83pceep = flags83pce | TIFeature.PYTHON
flags84pcepy = flags84pce | TIFeature.PYTHON
flags82aep = flags83pceep | {3: 0}

TI_82 = TIModel("TI-82", flags82, "**TI82**", b'\x00')
TI_83 = TIModel("TI-83", flags83, "**TI83**", b'\x00')
TI_82A = TIModel("TI-82A", flags82a, "**TI83F*", b'\x0B')
TI_82P = TIModel("TI-82+", flags83p, "**TI83F*", b'\x00')
TI_83P = TIModel("TI-83+", flags83p, "**TI83F*", b'\x04')
TI_84P = TIModel("TI-84+", flags84p, "**TI83F*", b'\x0A')
TI_84T = TIModel("TI-84+T", flags84p, "**TI83F*", b'\x1B')
TI_84PCSE = TIModel("TI-84+CSE", flags84pcse, "**TI83F*", b'\x0F')
TI_84PCE = TIModel("TI-84+CE", flags84pce, "**TI83F*", b'\x13')
TI_84PCEPY = TIModel("TI-84+CEPY", flags84pcepy, "**TI83F*", b'\x13')
TI_83PCE = TIModel("TI-83PCE", flags83pce, "**TI83F*", b'\x13')
TI_83PCEEP = TIModel("TI-83PCEEP", flags83pceep, "**TI83F*", b'\x13')
TI_82AEP = TIModel("TI-82AEP", flags82aep, "**TI83F*", b'\x00')

MODELS = [TI_82, TI_83, TI_82A, TI_82P, TI_83P,
          TI_84P, TI_84T, TI_84PCSE, TI_84PCE, TI_84PCEPY,
          TI_83PCE, TI_83PCEEP, TI_82AEP]


__all__ = ["TI_82", "TI_83", "TI_82A", "TI_82P", "TI_83P",
           "TI_84P", "TI_84T", "TI_84PCSE", "TI_84PCE", "TI_83PCE", "TI_84PCEPY",
           "TI_83PCE", "TI_83PCEEP", "TI_82AEP",
           "MODELS", "TIFeature", "TIModel"]

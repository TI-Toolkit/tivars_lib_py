class TIModel:
    def __init__(self, name: str, flags: int, magic: str, product_id: bytes):
        self.name = name
        self.flags = flags
        self.magic = magic
        self.product_id = product_id

    def __str__(self):
        return self.name

    def has(self, feature: int):
        return self.flags & feature


class TIFeature:
    NONE = 0
    DEFAULT = 1 << 0
    COMPLEX = 1 << 1
    FLASH = 1 << 2
    APPS = 1 << 3
    CLOCK = 1 << 4
    COLOR = 1 << 5
    EZ80 = 1 << 6
    EXACT_MATH = 1 << 7
    PYTHON = 1 << 8


FEATURES = [TIFeature.NONE, TIFeature.DEFAULT, TIFeature.COMPLEX, TIFeature.FLASH, TIFeature.APPS,
            TIFeature.CLOCK, TIFeature.COLOR, TIFeature.EZ80, TIFeature.EXACT_MATH, TIFeature.PYTHON]


flags82 = 0 | TIFeature.DEFAULT
flags83 = flags82 | TIFeature.COMPLEX
flags82a = flags83 | TIFeature.FLASH
flags83p = flags82a | TIFeature.APPS
flags84p = flags83p | TIFeature.CLOCK
flags84pcse = flags84p | TIFeature.COLOR
flags84pce = flags84pcse | TIFeature.EZ80
flags83pce = flags84pce | TIFeature.EXACT_MATH
flags83pceep = flags83pce | TIFeature.PYTHON
flags84pcepy = flags84pce | TIFeature.PYTHON
flags82aep = flags83pceep & ~TIFeature.APPS

TI_82 = TIModel("82", flags82, "**TI82**", b'\x00')
TI_83 = TIModel("83", flags83, "**TI83**", b'\x00')
TI_82a = TIModel("82A", flags82a, "**TI83F*", b'\x0B')
TI_82p = TIModel("82+", flags83p, "**TI83F*", b'\x00')
TI_83p = TIModel("83+", flags83p, "**TI83F*", b'\x04')
TI_84p = TIModel("84+", flags84p, "**TI83F*", b'\x0A')
TI_84t = TIModel("84+T", flags84p, "**TI83F*", b'\x1B')
TI_84pcse = TIModel("84+CSE", flags84pcse, "**TI83F*", b'\x0F')
TI_84pce = TIModel("84+CE", flags84pce, "**TI83F*", b'\x13')
TI_84pcet = TIModel("84+CET", flags84pce, "**TI83F*", b'\x13')
TI_84pcetpy = TIModel("84+CETPE", flags84pcepy, "**TI83F*", b'\x13')
TI_84pcepy = TIModel("84+CEPy", flags84pcepy, "**TI83F*", b'\x13')
TI_83pce = TIModel("83PCE", flags83pce, "**TI83F*", b'\x13')
TI_83pceep = TIModel("83PCEEP", flags83pceep, "**TI83F*", b'\x13')
TI_82aep = TIModel("82AEP", flags82aep, "**TI83F*", b'\x00')

MODELS = [TI_82, TI_83, TI_82a, TI_82p, TI_83p,
          TI_84p, TI_84t, TI_84pcse, TI_84pce, TI_84pcet, TI_84pcetpy, TI_84pcepy,
          TI_83pce, TI_83pceep, TI_82aep]


__all__ = ["TI_82", "TI_83", "TI_82a", "TI_82p", "TI_83p",
           "TI_84p", "TI_84t", "TI_84pcse", "TI_84pce", "TI_83pce", "TI_84pcet", "TI_84pcetpy", "TI_84pcepy",
           "TI_83pce", "TI_83pceep", "TI_82aep",
           "MODELS", "TIFeature", "FEATURES", "TIModel"]

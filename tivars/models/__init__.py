class TIModel:
    def __init__(self, name: str, flags: int, signature: str):
        self.name = name
        self.flags = flags
        self.signature = signature.encode('utf8')

    def has(self, feature: int):
        return self.flags & feature


class TIFeatures:
    NONE = 0
    DEFAULT = 1 << 0
    COMPLEX = 1 << 1
    FLASH = 1 << 2
    APPS = 1 << 3
    CLOCK = 1 << 4
    COLOR = 1 << 5
    EZ80 = 1 << 6
    EXACT_MATH = 1 << 7


features = [TIFeatures.NONE, TIFeatures.DEFAULT, TIFeatures.COMPLEX, TIFeatures.FLASH,
            TIFeatures.APPS, TIFeatures.CLOCK, TIFeatures.COLOR, TIFeatures.EZ80, TIFeatures.EXACT_MATH]


TI_82 = TIModel("82", flags82 := TIFeatures.DEFAULT, "**TI82**")
TI_83 = TIModel("83", flags83 := flags82 | TIFeatures.COMPLEX, "**TI83**")
TI_82a = TIModel("82a", flags82a := flags83 | TIFeatures.FLASH, "**TI83F*")
TI_83p = TIModel("83+", flags83p := flags82a | TIFeatures.APPS, "**TI83F*")
TI_84p = TIModel("84+", flags84p := flags83p | TIFeatures.CLOCK, "**TI83F*")
TI_84pcse = TIModel("84+CSE", flags84pcse := flags84p | TIFeatures.COLOR, "**TI83F*")
TI_84pce = TIModel("84+CE", flags84pce := flags84pcse | TIFeatures.EZ80, "**TI83F*")
TI_83pce = TIModel("83PCE", flags83pce := flags84pce | TIFeatures.EXACT_MATH, "**TI83F*")

models = [TI_82, TI_83, TI_82a, TI_83p, TI_84p, TI_84pcse, TI_84pce, TI_83pce]


__all__ = ["TI_82", "TI_83", "TI_82a", "TI_83p", "TI_84p", "TI_84pcse", "TI_84pce", "TI_83pce", "models",
           "TIFeatures", "features", "TIModel"]

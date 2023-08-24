from functools import total_ordering

from ..flags import *
from ..tokenizer.tokens.scripts import OsVersion, OsVersions, Tokens, TokenTrie
from ..tokenizer.tokens.scripts.parse import MODEL_ORDER


@total_ordering
class TIModel:
    MODELS = []

    def __init__(self, name: str, features: 'TIFeature', magic: str, product_id: int, lang: str):
        self._name = name
        self._features = TIFeature(features)
        self._magic = magic
        self._product_id = product_id
        self._lang = lang

        with open("tivars/tokenizer/tokens/8X.xml", encoding="UTF-8") as file:
            self._tokens = Tokens.from_xml_string(file.read(), self.OS("latest"))

        self._trie = {}
        for lang in self._tokens.langs:
            self._trie[lang] = TokenTrie.from_tokens(self._tokens, lang)

        self._trie[None] = self._trie["en"]

    def __eq__(self, other):
        return str(self) == str(other)

    def __ge__(self, other):
        return self.order >= other.order

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    @property
    def features(self) -> 'TIFeature':
        return self._features

    @property
    def lang(self) -> str:
        return self._lang

    @property
    def magic(self) -> str:
        return self._magic

    @property
    def name(self) -> str:
        return self._name

    @property
    def order(self) -> int:
        return MODEL_ORDER[self._name]

    @property
    def product_id(self) -> int:
        return self._product_id

    @property
    def tokens(self) -> Tokens:
        return self._tokens

    def get_trie(self, lang: str = None) -> TokenTrie:
        return self._trie[lang]

    def has(self, feature: 'TIFeature'):
        return feature in self._features

    def OS(self, version: str = "") -> OsVersion:
        return OsVersion(self.name, version)


class TIFeature(Flags):
    Complex = {0: 1}
    Flash = {1: 1}
    Apps = {2: 1}
    Clock = {3: 1}
    Color = {4: 1}
    ez80 = {5: 1}
    ExactMath = {6: 1}
    Python = {7: 1}


features82 = {}
features83 = features82 | TIFeature.Complex
features82a = features83 | TIFeature.Flash
features83p = features82a | TIFeature.Apps
features84p = features83p | TIFeature.Clock
features84pcse = features84p | TIFeature.Color
features84pce = features84pcse | TIFeature.ez80
features83pce = features84pce | TIFeature.ExactMath
features83pceep = features83pce | TIFeature.Python
features84pcepy = features84pce | TIFeature.Python
features82aep = features83pceep | {2: 0}

it = iter(MODEL_ORDER)
next(it)

TIModel.MODELS = [
    TI_82 := TIModel(next(it), features82, "**TI82**", 0x00, "en"),

    TI_83 := TIModel(next(it), features83, "**TI83**", 0x00, "en"),
    TI_82ST := TIModel(next(it), features83, "**TI83**", 0x00, "en"),
    TI_82ST_fr := TIModel(next(it), features83, "**TI83**", 0x00, "fr"),
    TI_76_fr := TIModel(next(it), features83, "**TI83**", 0x00, "fr"),

    TI_83P := TIModel(next(it), features83p, "**TI83F*", 0x04, "en"),
    TI_83PSE := TIModel(next(it), features83p, "**TI83F*", 0x04, "en"),
    TI_83P_fr := TIModel(next(it), features83p, "**TI83F*", 0x04, "fr"),
    TI_82P := TIModel(next(it), features83p, "**TI83F*", 0x04, "fr"),

    TI_84P := TIModel(next(it), features84p, "**TI83F*", 0x0A, "en"),
    TI_84PSE := TIModel(next(it), features84p, "**TI83F*", 0x0A, "en"),
    TI_83P_fr_USB := TIModel(next(it), features84p, "**TI83F*", 0x0A, "fr"),
    TI_84P_fr := TIModel(next(it), features84p, "**TI83F*", 0x0A, "fr"),
    TI_84PPSE := TIModel(next(it), features84p, "**TI83F*", 0x0A, "en"),

    TI_82A := TIModel(next(it), features82a, "**TI83F*", 0x0B, "fr"),
    TI_84PT := TIModel(next(it), features84p, "**TI83F*", 0x1B, "en"),

    TI_84PCSE := TIModel(next(it), features84pcse, "**TI83F*", 0x0F, "en"),

    TI_84PCE := TIModel(next(it), features84pce, "**TI83F*", 0x13, "en"),
    TI_84PCET := TIModel(next(it), features84pce, "**TI83F*", 0x13, "en"),
    TI_83PCE := TIModel(next(it), features83pce, "**TI83F*", 0x13, "fr"),
    TI_83PCEEP := TIModel(next(it), features83pceep, "**TI83F*", 0x13, "fr"),
    TI_84PCEPY := TIModel(next(it), features84pcepy, "**TI83F*", 0x13, "en"),
    TI_84PCETPE := TIModel(next(it), features84pcepy, "**TI83F*", 0x13, "en"),
    TI_82AEP := TIModel(next(it), features82aep, "**TI83F*", 0x00, "fr"),
]

__all__ = ["TI_82",
           "TI_83", "TI_82ST", "TI_82ST_fr", "TI_76_fr",
           "TI_83P", "TI_83PSE", "TI_83P_fr", "TI_82P",
           "TI_84P", "TI_84PSE", "TI_83P_fr_USB", "TI_84P_fr", "TI_84PPSE",
           "TI_84PT", "TI_82A",
           "TI_84PCSE",
           "TI_84PCE", "TI_84PCET", "TI_83PCE", "TI_83PCEEP", "TI_84PCEPY", "TI_84PCETPE", "TI_82AEP",
           "TIFeature", "TIModel", "OsVersion", "OsVersions"]

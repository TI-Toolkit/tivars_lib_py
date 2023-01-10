from tivars.models import *
from tivars.tokenizer import encode, decode
from tivars.tokenizer.tokens import *
from ..var import TIVar


class TIProgram(TIVar):
    extensions = {
        TI_82: "82p",
        TI_83: "83p",
        TI_82a: "8xp",
        TI_82p: "8xp",
        TI_83p: "8xp",
        TI_84p: "8xp",
        TI_84t: "8xp",
        TI_84pcse: "8xp",
        TI_84pce: "8xp",
        TI_84pcet: "8xp",
        TI_84pcetpy: "8xp",
        TI_84pcepy: "8xp",
        TI_83pce: "8xp",
        TI_83pceep: "8xp",
        TI_82aep: "8xp"
    }

    tokens = {
        TI_82: (TI82_TOKENS, TI82_BYTES),
        TI_83: (TI83_TOKENS, TI83_BYTES),
        TI_82a: (TI83_TOKENS, TI83_BYTES),
        TI_83p: (TI83_TOKENS, TI83_BYTES),
        TI_84p: (TI83_TOKENS, TI83_BYTES),
        TI_84t: (TI83_TOKENS, TI83_BYTES),
        TI_84pcse: (CSE_TOKENS, CSE_BYTES),
        TI_84pce: (CE_TOKENS, CE_BYTES),
        TI_84pcet: (CE_TOKENS, CE_BYTES),
        TI_84pcetpy: (CE_TOKENS, CE_BYTES),
        TI_84pcepy: (CE_TOKENS, CE_BYTES),
        TI_83pce: (CE_TOKENS, CE_BYTES),
        TI_83pceep: (CE_TOKENS, CE_BYTES),
        TI_82aep: (CE_TOKENS, CE_BYTES)
    }

    type_id = b'\x05'

    def load_string(self, string: str):
        token_map = self.tokens[self.model][0]
        self.data = encode(string, token_map)

    def string(self) -> str:
        byte_map = self.tokens[self.model][1]
        return decode(self.data, byte_map)


class TIProtectedProgram(TIProgram):
    type_id = b'\x06'


__all__ = ["TIProgram", "TIProtectedProgram"]

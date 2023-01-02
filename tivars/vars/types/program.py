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

    type_id = b'\x05'

    def dumps(self) -> str:
        byte_map = CE_BYTES if self.model in (TI_83pce, TI_84pce, TI_84pcet, TI_84pcetpy, TI_84pcepy) else CSE_BYTES
        return decode(self.data, byte_map)

    def loads(self, string: str):
        token_map = CE_TOKENS if self.model in (TI_83pce, TI_84pce, TI_84pcet, TI_84pcetpy, TI_84pcepy) else CSE_TOKENS
        self.data = encode(string, token_map)


class TIProtectedProgram(TIProgram):
    type_id = b'\x06'


__all__ = ["TIProgram", "TIProtectedProgram"]

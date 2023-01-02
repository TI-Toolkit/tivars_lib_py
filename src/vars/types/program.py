from src.models.models import *
from src.tokenizer.tokens import *

from src.tokenizer import tokenize
from ..var import TIVar


class TIProgram(TIVar):
    extensions = {
        TI_82: "82p",
        TI_83: "83p",
        TI_82a: "8xp",
        TI_83p: "8xp",
        TI_84p: "8xp",
        TI_84pcse: "8xp",
        TI_84pce: "8xp",
        TI_83pce: "8xp"
    }

    type_id = b'\x05'

    def loads(self, string: str):
        tokens = CE_TOKENS if self.model in (TI_83pce, TI_84pce) else CSE_TOKENS
        self.data = tokenize(string, tokens)


__all__ = ["TIProgram"]

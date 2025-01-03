"""
Token objects
"""


from tivars.tokens.scripts import *


class TIToken(Token):
    """
    Interface extension for the token sheets base ``Token`` container

    TITokens can be fetched by bytes or recognized names from a `TITokens` container attached to a `TIModel`.
    Instantiating your own `TIToken` is not recommended.
    """

    def __init__(self, token: Token):
        super().__init__(token.bits, token.langs, token.attrs, token.since, token.until)

        self.translation = self.langs[None] = self.langs["en"]

    def __repr__(self) -> str:
        return f"<{self.display} ({self.escape})>"

    @property
    def accessible(self) -> str:
        return self.translation.accessible

    @property
    def display(self) -> str:
        return self.translation.display

    @property
    def escape(self) -> str:
        return rf"\{'x' if len(self.bits) == 1 else 'u'}{self.bits.hex()}"

    def names(self) -> list[str]:
        return self.translation.names()


class IllegalToken(TIToken):
    def __init__(self, bits: bytes):
        self.bits = bits

        super().__init__(Token(bits, {"en": Translation(b'?', "?", self.escape, [])},
                               {"illegal": "true"}))


__all__ = ["TIToken", "IllegalToken"]

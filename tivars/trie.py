from tivars.tokens.scripts import *
from .token import TIToken


class TITokenTrie:
    """
    Trie for tokenizing text based on ``tivars.tokens.scripts.TokenTrie``
    """

    def __init__(self):
        self.token = None
        self.children = {}

    def insert(self, token: TIToken, lang: str = None):
        """
        Inserts the names of a `TIToken` into the trie in a given language

        :param token: The token to insert
        :param lang: The language to insert names from (defaults to English, ``en``)
        """

        if lang and lang not in token.langs:
            raise ValueError(f"lang '{lang}' not found or not yet supported")

        for name in token.langs[lang].names() if lang else token.names():
            current = self
            for char in name:
                if char not in current.children:
                    current.children[char] = self.__class__()

                current = current.children[char]

            current.token = token

    @classmethod
    def from_tokens(cls, tokens: 'TITokens', lang: str = None):
        """
        Inserts all tokens from a `TITokens` container into the trie

        :param tokens: The tokens to insert
        :param lang: The language to insert names from (defaults to English, ``en``)
        """

        if lang and lang not in tokens.langs:
            raise ValueError(f"lang '{lang}' not found or not yet supported")

        root = cls()
        for token in tokens.bytes.values():
            root.insert(token, lang)

        return root

    def match(self, string: str) -> list[tuple[TIToken, str]]:
        """
        Finds all tokens which can be parsed from a given input string

        Each token is returned with the portion of the input string still remaining.
        Output is sorted by decreasing length of the consumed input.

        :return: A list of tuples each containing a `TIToken` and its remaining input
        """

        tokens = []

        if string and string[0] in self.children:
            tokens += self.children[string[0]].match(string[1:])

        if self.token:
            tokens.append((self.token, string))

        return tokens


class TITokens:
    """
    Data class for storing collections of `TIToken` instances based on ``tivars.tokens.scripts.Tokens``

    `TIToken` instances may be obtained from various maps:

        - The byte map is indexed by token bytes.
        - The lang map is indexed by language code, then token name.
        - The name map is indexed by token name, regardless of language.

    The byte and name maps may be accessed via `__getitem__`.

    Additionally, a trie map contains a `TITokenTrie` for each language, indexed by language code.
    """

    def __init__(self, tokens: Tokens):
        self.bytes = {bits: TIToken(token) for bits, token in tokens.bytes.items()}
        self.langs = {lang: {name: self.bytes[bits] for name, bits in tokens.langs[lang].items()}
                      for lang in tokens.langs}

        # Flattened name index (probably won't have any clashes)
        self.names = {name: token for tokens in self.langs.values() for name, token in tokens.items()}

        # Tries
        self.tries = {lang: TITokenTrie.from_tokens(self, lang) for lang in self.langs}

        self.langs[None] = self.langs["en"]
        self.tries[None] = self.tries["en"]

    def __getitem__(self, item: bytes | str) -> TIToken:
        if isinstance(item, bytes):
            return self.bytes[item]

        elif isinstance(item, str):
            return self.names[item]

        raise KeyError(item)


__all__ = ["TITokenTrie", "TITokens"]

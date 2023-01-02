import xml.parsers.expat

from collections import namedtuple


TokenAttributes = namedtuple("TokenAttributes", ["bytes", "terminator"])
TokenMap = dict[str, TokenAttributes]


def load_tokens_xml(filename: str) -> TokenMap:
    def load_token(name, attributes):
        nonlocal curr_name
        nonlocal curr_bytes

        match name:
            case "Token":
                curr_bytes += bytearray([int(attributes["byte"][1:], 16)])
                if "string" in attributes:
                    curr_name = attributes["string"]
                    if curr_name == "\\n":
                        curr_name = "\n"

                    tokens[curr_name] = TokenAttributes(bytes=curr_bytes,
                                                        terminator=attributes.get("stringTerminator", False))

            case "Alt":
                if curr_name is None:
                    raise ValueError("Invalid XML provided")

                tokens[attributes["string"]] = tokens[curr_name]

    def close_token(name):
        nonlocal curr_name
        nonlocal curr_bytes

        match name:
            case "Token":
                curr_name = None
                curr_bytes = curr_bytes[:-1]

    tokens = {}

    curr_name = None
    curr_bytes = bytearray()

    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = load_token
    parser.EndElementHandler = close_token

    with open(filename, encoding="utf8") as file:
        parser.Parse(file.read())

    return tokens


__all__ = ["load_tokens_xml", "TokenMap", "TokenAttributes"]

import xml.parsers.expat

from collections import namedtuple


TokenAttributes = namedtuple("TokenAttributes", ["bytes", "terminator"])
TokenMap = dict[str, TokenAttributes]
ByteMap = dict[bytes, list[str]]


def load_tokens_xml(filename: str) -> tuple[TokenMap, ByteMap]:
    def load_token(name, attributes):
        nonlocal curr_name
        nonlocal curr_bytes

        match name:
            case "Token":
                curr_bytes += bytes([int(attributes["byte"][1:], 16)])
                if "string" in attributes:
                    curr_name = attributes["string"]
                    if curr_name == "\\n":
                        curr_name = "\n"

                    token_map[curr_name] = TokenAttributes(bytes=curr_bytes,
                                                           terminator=attributes.get("stringTerminator", False))
                    byte_map[curr_bytes] = [curr_name]

            case "Alt":
                if curr_name is None:
                    raise ValueError("Invalid XML provided.")

                token_map[attributes["string"]] = token_map[curr_name]
                byte_map[curr_bytes].append(attributes["string"])

    def close_token(name):
        nonlocal curr_name
        nonlocal curr_bytes

        match name:
            case "Token":
                curr_name = None
                curr_bytes = curr_bytes[:-1]

    token_map = {}
    byte_map = {}

    curr_name = None
    curr_bytes = bytes()

    parser = xml.parsers.expat.ParserCreate()
    parser.StartElementHandler = load_token
    parser.EndElementHandler = close_token

    with open(filename, encoding="utf8") as file:
        parser.Parse(file.read())

    return token_map, byte_map


__all__ = ["load_tokens_xml", "TokenMap", "TokenAttributes", "ByteMap"]

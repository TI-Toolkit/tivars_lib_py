import os.path as path

from tivars.tokenizer import load_tokens_xml


_dir = path.dirname(__file__)

AXE_TOKENS, AXE_BYTES = load_tokens_xml(path.join(_dir, "tokens/Axe.xml"))

CE_TOKENS, CE_BYTES = load_tokens_xml(path.join(_dir, "tokens/TI-84+CE.xml"))

CSE_TOKENS, CSE_BYTES = load_tokens_xml(path.join(_dir, "tokens/TI-84+CSE.xml"))

GRAMMER_TOKENS, GRAMMER_BYTES = load_tokens_xml(path.join(_dir, "tokens/Grammer.xml"))

NOLIB_TOKENS, NOLIB_BYTES = load_tokens_xml(path.join(_dir, "tokens/NoLib.xml"))

PRIZM_TOKENS, PRIZM_BYTES = load_tokens_xml(path.join(_dir, "tokens/Prizm.xml"))


__all__ = ["AXE_TOKENS", "CE_TOKENS", "CSE_TOKENS", "GRAMMER_TOKENS", "NOLIB_TOKENS", "PRIZM_TOKENS",
           "AXE_BYTES", "CE_BYTES", "CSE_BYTES", "GRAMMER_BYTES", "NOLIB_BYTES", "PRIZM_BYTES"]
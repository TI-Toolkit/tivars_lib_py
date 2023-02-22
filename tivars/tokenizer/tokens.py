import os.path as path

from tivars.tokenizer.parse import load_tokens_xml


_dir = path.dirname(__file__)

AXE_TOKENS, AXE_BYTES = load_tokens_xml(path.join(_dir, "tokens/Axe.xml"))

CE_TOKENS, CE_BYTES = load_tokens_xml(path.join(_dir, "tokens/CE-BASIC.xml"))

CSE_TOKENS, CSE_BYTES = load_tokens_xml(path.join(_dir, "tokens/CSE-BASIC.xml"))

GRAMMER_TOKENS, GRAMMER_BYTES = load_tokens_xml(path.join(_dir, "tokens/Grammer.xml"))

TI83_TOKENS, TI83_BYTES = load_tokens_xml(path.join(_dir, "tokens/TI-83-BASIC.xml"))

PRIZM_TOKENS, PRIZM_BYTES = load_tokens_xml(path.join(_dir, "tokens/Prizm.xml"))

TI82_TOKENS, TI82_BYTES = load_tokens_xml(path.join(_dir, "tokens/TI-82-BASIC.xml"))

TI73_TOKENS, TI73_BYTES = load_tokens_xml(path.join(_dir, "tokens/TI-73-BASIC.xml"))


__all__ = ["AXE_TOKENS", "CE_TOKENS", "CSE_TOKENS", "GRAMMER_TOKENS",
           "TI83_TOKENS", "PRIZM_TOKENS", "TI82_TOKENS", "TI73_TOKENS",
           "AXE_BYTES", "CE_BYTES", "CSE_BYTES", "GRAMMER_BYTES",
           "TI83_BYTES", "PRIZM_BYTES", "TI82_BYTES", "TI73_BYTES"]

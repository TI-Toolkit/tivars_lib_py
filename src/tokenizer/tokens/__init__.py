from ..parse import load_tokens_xml

AXE_TOKENS = load_tokens_xml(".\\tokenizer\\tokens\\Axe.xml")

CE_TOKENS = load_tokens_xml(".\\tokenizer\\tokens\\TI-84+CE.xml")

CSE_TOKENS = load_tokens_xml(".\\tokenizer\\tokens\\TI-84+CSE.xml")

GRAMMER_TOKENS = load_tokens_xml(".\\tokenizer\\tokens\\Grammer.xml")

NOLIB_TOKENS = load_tokens_xml(".\\tokenizer\\tokens\\NoLib.xml")

PRIZM_TOKENS = load_tokens_xml(".\\tokenizer\\tokens\\Prizm.xml")


__all__ = ["AXE_TOKENS", "CE_TOKENS", "CSE_TOKENS", "GRAMMER_TOKENS", "NOLIB_TOKENS", "PRIZM_TOKENS"]

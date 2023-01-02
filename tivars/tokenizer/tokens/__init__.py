from ..parse import load_tokens_xml

AXE_TOKENS, AXE_BYTES = load_tokens_xml("./tivars/tokenizer/tokens/Axe.xml")

CE_TOKENS, CE_BYTES = load_tokens_xml("./tivars/tokenizer/tokens/TI-84+CE.xml")

CSE_TOKENS, CSE_BYTES = load_tokens_xml("./tivars/tokenizer/tokens/TI-84+CSE.xml")

GRAMMER_TOKENS, GRAMMER_BYTES = load_tokens_xml("./tivars/tokenizer/tokens/Grammer.xml")

NOLIB_TOKENS, NOLIB_BYTES = load_tokens_xml("./tivars/tokenizer/tokens/NoLib.xml")

PRIZM_TOKENS, PRIZM_BYTES = load_tokens_xml("./tivars/tokenizer/tokens/Prizm.xml")


__all__ = ["AXE_TOKENS", "CE_TOKENS", "CSE_TOKENS", "GRAMMER_TOKENS", "NOLIB_TOKENS", "PRIZM_TOKENS",
           "AXE_BYTES", "CE_BYTES", "CSE_BYTES", "GRAMMER_BYTES", "NOLIB_BYTES", "PRIZM_BYTES"]

class TIModel:
    def __init__(self, name: str, flags: int, signature: str):
        self.name = name
        self.flags = flags
        self.signature = signature.encode('utf8')

    def has(self, feature: int):
        return self.flags & feature


__all__ = ["TIModel"]

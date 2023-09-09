import io

from warnings import warn

from tivars.models import *
from ..data import *
from ..var import TIEntry, SizedEntry
from .gdb import TIGraphedEquation


class TIGroup(SizedEntry, register=True):
    _T = 'TIGroup'

    extensions = {
        None: "8xg",
        TI_82: "82g",
        TI_83: "83g",
        TI_83P: "8xg"
    }

    _type_id = 0x17

    def __init__(self, init=None, *,
                 for_flash: bool = True, name: str = "GROUP1",
                 version: int = None, archived: bool = True,
                 data: bytes = None):

        super().__init__(init, for_flash=for_flash, name=name, version=version, archived=archived, data=data)

    @staticmethod
    def group(entries: list[TIEntry], *, name: str = "GROUP1") -> 'TIGroup':
        if not entries:
            return TIGroup(name=name)

        group = TIGroup(for_flash=entries[0].meta_length > TIEntry.base_meta_length, name=name)

        for entry in entries:
            name = entry.raw.name.rstrip(b'\x00')
            vat = bytearray([entry.type_id, 0, entry.version, 0, 0, entry.archived])

            if isinstance(entry, TIGraphedEquation):
                vat[0] |= entry.raw.flags

            match entry.type_id:
                case 0x05 | 0x06 | 0x15 | 0x17:
                    vat += [len(name), *name]

                case 0x01 | 0x0D:
                    vat += [len(name) + 1, *name, 0]

                case _:
                    vat += name.ljust(3, b'\x00')

            group.data += vat
            group.data += entry.calc_data

        return group

    @Loader[list]
    def load_from_entries(self, entries: list[TIEntry]):
        self.data = self.group(entries).data

    def ungroup(self, *, model: TIModel = None) -> list[TIEntry]:
        data = io.BytesIO(self.data[:])
        entries = []

        index = 1
        while type_byte := data.read(1):
            _, version = data.read(2)

            match type_id := type_byte[0] & 15:
                case 0x05 | 0x06 | 0x15 | 0x17:
                    *_, page, length = data.read(4)

                    if length > 8:
                        warn(f"The name length of entry #{index} ({length}) exceeds eight.",
                             BytesWarning)

                    name = data.read(length)

                case 0x01 | 0x0D:
                    *_, page, length = data.read(4)

                    if length > 7:
                        warn(f"The name length of entry #{index} ({length - 2}), a list, exceeds five.",
                             BytesWarning)

                    name = data.read(length - 1)
                    data.read(1)

                case _:
                    *_, page = data.read(3)
                    name = data.read(3)

            model = model or TI_84PCE
            entry = TIEntry(for_flash=model.has(TIFeature.Flash), version=version, archived=page > 0)
            entry.type_id = type_id
            entry.coerce()

            entry.raw.name = name.ljust(8, b'\x00')
            entry.load_data_section(data)

            if isinstance(entry, TIGraphedEquation):
                entry.raw.flags = type_byte

            entries.append(entry)

        return entries

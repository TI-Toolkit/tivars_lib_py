from .data import *
from .header import *


class TIFile(Dock):
    """
    Base class for all TI files

    A file is composed of a header (or perhaps two, or three) and any number of entries (though most have only one).
    """

    def __init__(self, *, components: list = None, data: bytes = None):
        """
        Creates an empty file with a specified name, header, and data

        :param components: A list of components composing this file (defaults to empty)
        :param data: The file's data (defaults to empty)
        """

        self.components = components or []

        if data:
            self.load_bytes(data)

    def __bool__(self) -> bool:
        """
        :return: Whether this var contains no entries
        """

        return not self.is_empty

    def __bytes__(self) -> bytes:
        """
        :return: The bytes contained in this var
        """

        return self.bytes()

    def __copy__(self) -> 'TIFile':
        """
        :return: A copy of this var
        """

        new = TIFile()
        new.load_bytes(self.bytes())
        return new

    def __eq__(self, other: 'TIFile'):
        """
        Determines if two files contain the same header and entries

        :param other: The var to check against
        :return: Whether this var is equal to ``other``
        """

        try:
            eq = self.__class__ == other.__class__ and len(self.components) == len(other.components)
            return eq and all(component == other_components
                              for component, other_components in zip(self.components, other.components))

        except AttributeError:
            return False

    def __len__(self):
        """
        :return: The total length of this var's bytes
        """

        return sum(map(len, self.components))

    @property
    def entry_length(self) -> int:
        """
        The total length of the var entries

        This should always be 57 less than the total var size.
        """

        return sum(len(entry) for entry in self.entries)

    @property
    def checksum(self) -> bytes:
        """
        The checksum for the var

        This is equal to the lower 2 bytes of the sum of all bytes in the entries.
        """

        return int.to_bytes(sum(sum(entry.bytes()) for entry in self.entries) & 0xFFFF, 2, 'little')

    @property
    def is_empty(self) -> bool:
        """
        :return: Whether this var contains no entries
        """

        return len(self.entries) == 0

    def add_entry(self, entry: TIEntry = None):
        """
        Adds an entry to this var

        :param entry: A `TIEntry` to add (defaults to an empty entry)
        """

        entry = entry or TIEntry()

        if not self.is_empty:
            if entry.meta_length != self.entries[0].meta_length:
                warn(f"The new entry has a conflicting meta length "
                     f"(expected {self.entries[0].meta_length}, got {entry.meta_length}).",
                     UserWarning)

        self.entries.append(entry)

    def clear(self):
        """
        Removes all components from this file
        """

        self.components.clear()

    def get_extension(self, model: TIModel = None) -> str:
        """
        Determines the file's extension based on its components and targeted model

        If there is only one entry, that entry's extension for the target model is used.
        Otherwise, ``.8xg`` is used.

        :param model: The model to target (defaults to this var's minimum model)
        :return: The var's file extension
        """

        model = model or self.get_min_model()

        if len(self.entries) != 1:
            return "8xg"

        elif model not in self.entries[0].extensions:
            warn(f"The {model} does not support this var type.",
                 UserWarning)

            return self.entries[0].extensions[None]

        else:
            return self.entries[0].extensions[model]

    def get_filename(self, model: TIModel = None) -> str:
        """
        Determines the var's filename based on its name, entries, and targeted model

        The filename is the concatenation of the var name and extension (see `TIVar.get_extension`).

        :param model: The model to target (defaults to this var's minimum model)
        :return: The var's filename
        """

        return f"{self.name}.{self.get_extension(model)}"

    def get_min_model(self) -> TIModel | None:
        """
        Determines the minimum model this var can target, or ``None`` if none exists

        :return: This var's minium model, or ``None``
        """

        return min(self.get_targets(), default=None)

    def get_targets(self) -> set[TIModel]:
        """
        Determines which model(s) this var can target

        A var targets the models that its header targets.

        See `TIVar.supported_by` to check models which this var _can_ be sent to.

        :return: A set of models that this var can target
        """

        return self._header.get_targets()

    def supported_by(self, model: TIModel) -> bool:
        """
        Determines whether a given model can support this var

        A var is supported by a model if its header and all its entries is.

        See `TIVar.targets` to check models which this var explicitly targets.

        :param model: The model to check support for
        :return: Whether ``model`` supports this var
        """

        return self._header.supported_by(model) and \
            all(entry.get_min_os() < model.OS("latest") for entry in self.entries)

    def load_bytes(self, data: bytes | BytesIO):
        """
        Loads a byte string or bytestream into this var

        :param data: The bytes to load
        """

        try:
            data = BytesIO(data.read())

        except AttributeError:
            data = BytesIO(data)

        # Read header
        self._header.load_bytes(data.read(53))
        entry_length = int.from_bytes(data.read(2), 'little')

        # Read entries
        self.clear()
        while entry_length > 0:
            self.add_entry()

            length = TIEntry.next_entry_length(data)
            self.entries[-1].load_bytes(entry_data := data.read(length))

            if len(entry_data) != length:
                warn(f"The data length of entry #{len(self.entries) - 1} ({type(self.entries[-1])}) is incorrect "
                     f"(expected {length}, got {len(entry_data)}).",
                     BytesWarning)

            entry_length -= length

        if entry_length < 0:
            warn(f"The total length of entries is incorrect (expected {self.entry_length + entry_length}, "
                 f"got {self.entry_length}).",
                 BytesWarning)

        # Read checksum
        checksum = data.read(2)

        # Check² sum
        if checksum != self.checksum:
            warn(f"The checksum is incorrect (expected {self.checksum}, got {checksum}).",
                 BytesWarning)

    def bytes(self):
        """
        :return: The bytes contained in this var
        """

        dump = self._header.bytes()
        dump += int.to_bytes(self.entry_length, 2, 'little')

        for entry in self.entries:
            dump += entry.bytes()

        dump += self.checksum
        return dump

    def load_var_file(self, file: BinaryIO):
        """
        Loads this var from a file given a file pointer

        :param file: A binary file to read from
        """

        self.load_bytes(file.read())

    @classmethod
    def open(cls, filename: str) -> 'TIVar':
        """
        Creates a new var from a file given a filename

        :param filename: A filename to open
        :return: The var stored in the file
        """

        with open(filename, 'rb') as file:
            return cls(data=file.read())

    def save(self, filename: str = None, model: TIModel = None):
        """
        Saves this var given a filename

        :param filename: A filename to save to (defaults to the var's name and extension)
        :param model: A `TIModel` to target (defaults this var's minimum model)
        """

        if model:
            for index, entry in enumerate(self.entries):
                if entry.get_min_os() > model.OS("latest"):
                    warn(f"Entry #{index + 1} ({type(entry)}) is not supported by {model}.",
                         UserWarning)

        with open(filename or self.get_filename(model), 'wb+') as file:
            file.write(self.bytes())
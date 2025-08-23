"""
TI Bundles

Thanks @Zaalane3!
"""

from io import BytesIO
from pathlib import Path
from warnings import catch_warnings, simplefilter, warn
from zipfile import ZipFile

from .data import *
from .file import *
from .models import *


class TIBundle(TIFile, register=True):
    """
    Interface for TI bundles

    A bundle is a zip file with some metadata and a checksum.
    """

    magics = ["PK\x03\x04"]

    def __init__(self, *, name: str = "BUNDLE", data: bytes = None):
        self._buffer = BytesIO()
        self.zipfile = None

        super().__init__(name=name, data=data)

    @property
    def comment(self) -> str:
        """
        This bundle's comment(s)
        """

        return self.metadata["bundle_comments"]

    @property
    def checksum(self) -> bytes:
        """
        The checksum for the bundle

        This is given as a sum of the CRC's of its files
        """

        return self.zipfile.read("_CHECKSUM")

    @property
    def metadata(self) -> dict[str, str]:
        """
        The metadata fields of the bundle
        """

        return dict(line.split(":", maxsplit=1) for line in self.zipfile.read("METADATA").decode().splitlines() if line)

    @property
    def model(self) -> TIModel:
        """
        The model this bundle targets
        """

        return TI_84PCE if self.metadata["bundle_target_device"] == "84CE" else TI_83PCE

    @property
    def target_type(self) -> str:
        """
        This bundle's target type
        """

        return self.metadata["bundle_target_type"]

    @property
    def version(self) -> int:
        """
        This bundle's format version (which is usually 1)
        """

        return int(self.metadata["bundle_format_version"])

    @staticmethod
    def bundle(files: list[TIFile], *, name: str = "BUNDLE", model: TIModel = TI_84PCE,
               comment: str = "Created with tivars_lib_py v0.9.2",
               target_type: str = "CUSTOM", version: int = 1) -> 'TIBundle':
        """
        Compress a list of `TIFile` objects into a bundle

        :param files: The files to bundle
        :param name: The name of the bundle (defaults to ``BUNDLE``)
        :param model: The model this bundle should target (defaults to the TI-84+CE)
        :param comment: A comment to attach to this bundle (defaults to a simple lib message)
        :param target_type: The target type for the bundle (defaults to ``CUSTOM``)
        :param version: The format version of the bundle (defaults to 1)
        :return: A bundle containing ``files`` with the specified metadata
        """

        buffer = BytesIO()
        archive = ZipFile(buffer, 'w', allowZip64=False)

        # Write files
        for file in files:
            archive.writestr(file.get_filename(model), file.bytes())

        # Write METADATA
        metadata = {
            "bundle_identifier": "TI Bundle",
            "bundle_format_version": str(version),
            "bundle_target_device": f"{TIBundle.get_extension(model)[1:]}CE",
            "bundle_target_type": target_type,
            "bundle_comments": comment or "N/A"
        }

        archive.writestr("METADATA", "".join(f"{key}:{value}\n" for key, value in metadata.items()))

        # Write checksum
        archive.writestr("_CHECKSUM", f"{sum(info.CRC for info in archive.infolist()) & 0xFFFFFFFF:x}\r\n".encode())
        archive.close()

        return TIBundle(name=name, data=buffer.getvalue())

    @classmethod
    def get_extension(cls, model: TIModel = TI_84PCE) -> str:
        if model in (TI_84PCE, TI_84PCET, TI_84PCEPY, TI_84PCETPE):
            return "b84"

        else:
            if model not in (TI_83PCE, TI_83PCEEP):
                warn(f"The {model} does not support this file.",
                     UserWarning)

            return "b83"

    def supported_by(self, model: TIModel) -> bool:
        with catch_warnings():
            try:
                simplefilter("error")
                self.get_extension(model)
                return True

            except UserWarning:
                return False

    def targets(self, model: TIModel) -> bool:
        with catch_warnings():
            try:
                simplefilter("error")
                return self.get_extension(model) == self.get_extension(self.model)

            except UserWarning:
                return False

    def unbundle(self) -> list[TIFile]:
        """
        Unzips a bundle into a ``list`` of its files

        :return: A ``list`` of the files stored in this bundle
        """

        return [TIFile(name=Path(name).stem, data=self.zipfile.open(name).read()) for name in self.zipfile.namelist()
                if name not in ("METADATA", "_CHECKSUM")]

    @Loader[bytes, bytearray, memoryview, BytesIO]
    def load_bytes(self, data: bytes | BytesIO):
        if hasattr(data, "read"):
            self._buffer.write(data.read())

        else:
            self._buffer.write(data)

        self.zipfile = ZipFile(self._buffer, 'r', allowZip64=False)

    def bytes(self) -> bytes:
        return self._buffer.getvalue()


__all__ = ["TIBundle"]

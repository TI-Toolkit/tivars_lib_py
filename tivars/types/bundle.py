import zipfile

bundle_metadata = {
    "b83": ("bundle_identifier:TI Bundle\n"
            "bundle_format_version:1\n"
            "bundle_target_device:83CE\n"
            "bundle_target_type:CUSTOM\n"
            "bundle_comments:N/A\n"),
    "b84": ("bundle_identifier:TI Bundle\n"
            "bundle_format_version:1\n"
            "bundle_target_device:84CE\n"
            "bundle_target_type:CUSTOM\n"
            "bundle_comments:N/A\n"),
}


class TIBundle:

    def __init__(self, name: str, *, ext: str = "b84"):
        self.zip = zipfile.ZipFile(name, 'w', allowZip64=False)
        self.ext = ext
        self.zip.writestr("METADATA", bundle_metadata[ext])

    def addFile(self, name: str, arcname: str):
        self.zip.write(name, arcname)

    def writeChecksum(self):
        checksum = 0
        for info in self.zip.infolist():
            checksum += info.CRC
        checksum &= 0xFFFFFFFF
        self.zip.writestr("_CHECKSUM", f"{checksum:x}\r\n")

    def close(self):
        self.zip.close()
import sys
from typing import Callable


class File:
    _fname: str
    _data: bytes

    def __init__(self, fname: str, data: bytes):
        self._fname = fname
        self._data = data

    def save(self):
        size_kb = len(self._data) // 1024
        print(f"{self._fname} ({size_kb} KB)")
        with open(self._fname, "wb") as f:
            f.write(self._data)


class FileTypeInfo:
    start_marker: bytes
    end_marker: bytes
    ext: str
    _validator: Callable[[bytes], bool]

    def __init__(self, ext: str, start_marker: bytes, end_marker: bytes, validator: Callable[[bytes], bool]):
        self.start_marker = start_marker
        self.end_marker = end_marker
        self.ext = ext
        self._validator = validator

    def validate(self, data: bytes):
        return self._validator(data)


class Extractor:
    _target_fname: str
    _file_type_info: FileTypeInfo
    _cnt: int

    def __init__(self, target_fname: str, file_type_info: FileTypeInfo):
        self._target_fname = target_fname
        self._file_type_info = file_type_info
        self._cnt = 0

    def extract(self):
        f = open(self._target_fname, "rb")
        buf: bytes = f.read()
        f.close()

        pos = 0
        while pos < len(buf):
            start = buf.find(self._file_type_info.start_marker, pos)
            stop = buf.find(self._file_type_info.end_marker, start)

            if start == -1 or stop == -1:
                break

            stop += len(self._file_type_info.end_marker)

            data = buf[start:stop]

            if self._file_type_info.validate(data):
                self.save(data)

            pos = stop

    def save(self, data: bytes):
        fname = f"{self._target_fname}_{self._cnt}.{self._file_type_info.ext}"
        f = File(fname, data)
        f.save()
        self._cnt += 1


def main(argv: list[str]):
    SOI = b"\xff\xd8"
    APP0 = b"\xff\xe0"
    EOI = b"\xff\xd9"

    def jpg_validator(data: bytes):
        return data[:2] == SOI and data[2:4] == APP0 and data[-2:] == EOI

    jpg_info = FileTypeInfo("jpg", SOI, EOI, jpg_validator)
    exjpg = Extractor(argv[1], jpg_info)
    exjpg.extract()


if __name__ == "__main__":
    main(sys.argv)

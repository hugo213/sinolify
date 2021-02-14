import hashlib
import os
import shutil
from typing import Dict, Optional


class ConversionMapping:
    find_directory: str
    replace_directory: str
    map: Dict[str, str]

    class FindError(BaseException):
        pass

    class ReplaceError(BaseException):
        pass

    def __init__(self, find_directory: str, replace_directory: str):
        self.find_directory = find_directory
        self.replace_directory = replace_directory
        self.build_mapping()

    @staticmethod
    def hash(file_path: str) -> str:
        return hashlib.md5(open(file_path, 'rb').read()).hexdigest()

    def build_mapping(self):
        self.map = dict()
        for filename in os.listdir(self.find_directory):
            path = os.path.join(self.find_directory, filename)
            self.map[self.hash(path)] = path

    def find(self, file_path: str) -> Optional[str]:
        h = self.hash(file_path)
        if h not in self.map:
            raise self.FindError()
        filename = os.path.basename(self.map[h])
        if filename.endswith('.ignore'):
            return None
        replace = os.path.join(self.replace_directory, filename)
        if not os.path.isfile(replace):
            raise self.ReplaceError()
        return replace

    def todo(self, file_path: str) -> str:
        h = self.hash(file_path)
        assert h not in self.map
        filename = h + os.path.splitext(file_path)[1]
        shutil.copy(file_path, os.path.join(self.find_directory, filename))
        shutil.copy(file_path, os.path.join(self.replace_directory, filename + '.todo'))
        return filename

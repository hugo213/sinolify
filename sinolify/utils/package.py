import re
import shutil
import zipfile
import tempfile
import os
from typing import Generator


class Package:
    """ Represents a task package archive.

    Package has a short string `ID`.
    Files inside the package can be referred to by package-root-relative
    *local paths*.
    """
    _source: str
    _tmp_dir: tempfile.TemporaryDirectory
    _id: str

    def __init__(self, *, zip: str = None, id: str = None):
        """ Creates or loads a package.

        The only requirement on the loaded task package is that the .zip file
        contains a single directory. Name of this directory is interpreted as
        the task ID.

        :param zip: If `zip` is specified, the package is loaded from the .zip
            file which path is `zip`.  If `id` is also specified, the loaded
            package ID is expected to match with `id`.

        :param id: If `id` is specified and `zip` is not, a new package with
            specified ID is created.
        """

        assert zip or id
        self._tmp_dir = tempfile.TemporaryDirectory()
        if zip:
            self._source = zip
            zipfile.ZipFile(zip, mode='r').extractall(self._tmp_dir.name)
            dirs = os.listdir(self._tmp_dir.name)
            assert len(dirs) == 1, 'One package directory expected'
            self._id = dirs[0]
            assert not id or self.id == id, 'Wrong task ID'
        elif id:
            self._id = id
            os.mkdir(os.path.join(self._tmp_dir.name, id), mode=0o755)

    @property
    def id(self) -> str:
        """ Returns task ID. """
        return self._id

    @property
    def root(self) -> str:
        """ Returns path of package's root directory. """
        return os.path.join(self._tmp_dir.name, self.id)

    def abspath(self, local_path: str) -> str:
        """ Converts a local path to an absolute path. """
        return os.path.join(self.root, local_path)

    def find(self, regex: str) -> Generator[str, None, None]:
        """ Yields all files which local paths match `regex`.

        :param regex: Regular expression to match paths with.
            Note that local paths contain no leading slash.
        """
        for root, dirs, files in os.walk(self.root):
            for name in files:
                path = os.path.relpath(os.path.join(root, name), self.root)
                if re.fullmatch(regex, path):
                    yield path

    def add(self, path: str, target: str) -> None:
        """ Adds a file to the package.

        :param path: Path of a file to add to the package.

        :param target: Local path for the target.
        """
        target_path = self.abspath(target)
        os.makedirs(os.path.dirname(target_path), exist_ok=True, mode=0o755)
        shutil.copyfile(path, target_path)

    def save(self, path: str, overwrite: bool = False) -> None:
        """ Exports a Package to a .zip file.

        :param path: Output .zip file.

        :param overwrite: If true, allows to overwrite output file.
        """
        zip = zipfile.ZipFile(path, mode=('x' if not overwrite else 'w'))
        for p in self.find('.*'):
            zip.write(self.abspath(p), os.path.join(self.id, p))
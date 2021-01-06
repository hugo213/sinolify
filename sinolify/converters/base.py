import re
from typing import Set, Generator, Callable

from sinolify.utils.log import log
from sinolify.utils.package import Package


class ConverterBase:
    """ A base class for *converters* operating on problem packages.

    A converter is a utility intended to simplify operations required to build
    one package (target) based on another package (source). The converter keeps
    track of the processed paths in the source package.
    """
    _source: Package
    _target: Package
    _processed: Set[str]

    def __init__(self, source: Package, target: Package):
        """ Instantiates a new converters.

        :param source: The source package.

        :param target: The target package.
        """
        self._source = source
        self._target = target
        self._processed = set()

    def find(self, regex: str) -> Generator[str, None, None]:
        """ Yields all local paths in the source package matching the regex.

        :param regex: Regex to match local paths with.

        :return: Paths of files matching the regex.
        """
        for p in self._source.find(regex):
            yield p

    def exists(self, regex: str) -> bool:
        """ Checks if a path matching regex exists.

        :param regex: Regex to match local paths with.

        :return: True if any path matches the regex
        """
        for _ in self.find(regex):
            return True
        return False

    def ignore(self, regex: str) -> None:
        """ Marks all matching paths as processed.

        :param regex: Regular expression to match paths with.
        """
        self._processed |= set(self.find(regex))

    def copy(self, regex: str,
             transform: Callable[[str], str] = (lambda path: path),
             condition: Callable[[str], bool] = (lambda path: True),
             ignore_processed: bool = False) -> int:
        """ Copies specified files from *source* to *target*.

        :param regex: Regex to match the paths in source with.

        :param transform: An optional function used to transform a source path
            into a target path.

        :param condition: An extra condition a matched path must satisfy to be
            copied.

        :param ignore_processed: If set, the files that are marked as processed
            are ignored.

        :return: Number of copied files.
        """
        copied = 0
        for path in self._source.find(regex):
            if condition(path) and (path not in self._processed or not ignore_processed):
                log.debug('%s -> %s', path, transform(path))
                self._target.add(self._source.abspath(path), transform(path))
                self._processed.add(path)
                copied += 1
        return copied

    def copy_rename(self, regex: str, repl: str,
                    condition: Callable[[str], bool] = (lambda path: True),
                    ignore_processed: bool = False) -> int:
        """ Copies files from *source* to *target* and renames them.

        The files are renamed using `re.replace` as specified by `regex` and
        `repl`.

        :param regex: Regex to match the paths with.

        :param repl: A replacement string. See `re.replace`.

        :param condition: An extra condition a matched path must satisfy to be
            copied.

        :param ignore_processed: If set, the files that are marked as processed
            are ignored.

        :return: Number of files copied.
        """
        transform = (lambda path: re.sub(regex, repl, path))
        return self.copy(regex, transform, condition, ignore_processed)

    def not_processed(self) -> Set[str]:
        """ Returns source paths that are not marked as processed.

        :return: Set of paths that are not yet processed.
        """
        return set(self._source.find(rf'.*')) - self._processed

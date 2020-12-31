import re
from typing import Set, Generator, Pattern, Callable

from sinolify.log import log, warning_assert, error_assert
from sinolify.package import Package


class Converter:
    _source: Package
    _target: Package
    _processed: Set[str] = set()

    def __init__(self, source: Package, target: Package):
        self._source = source
        self._target = target

    def find(self, regex: str) -> Generator[str, None, None]:
        for p in self._source.find(regex):
            yield p

    def ignore(self, regex: str) -> None:
        self._processed |= set(self.find(regex))

    def copy(self, regex: str,
             transform: Callable[[str], str] = (lambda path: path),
             condition: Callable[[str], bool] = (lambda path: True),
             ignore_processed: bool = False) -> int:
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
                    ignore_processed: bool = False):
        transform = (lambda path: re.sub(regex, repl, path))
        return self.copy(regex, transform, condition, ignore_processed)

    def not_processed(self):
        return set(self._source.find(rf'.*')) - self._processed


class SowaToSinolConverter(Converter):
    _prog_ext = '(?:cpp|c|cc|pas)'

    @property
    def id(self):
        return self._source.id

    def make_tests(self):
        log.debug('Making tests')
        error_assert(self.copy(rf'in/{self.id}\d+[a-z]*.in') > 0,
                          'No input files')
        warning_assert(self.copy(rf'out/{self.id}\d+[a-z]*.out') > 0,
                            'No output files')

    def make_doc(self):
        log.debug('Making docs')
        error_assert(self.copy(rf'doc/{self.id}\.pdf') > 0,
                          'No problem statement')
        warning_assert(self.copy_rename(rf'desc/{self.id}\.tex', f'doc/{self.id}zad.tex'),
                            'No statement source')
        self.ignore(f'desc/{self.id}_opr.tex')
        self.copy_rename(rf'desc/(.*\.(?:pdf|tex))', rf'doc/\1', ignore_processed=True)

    def make_solutions(self):
        log.debug('Making solutions')
        error_assert(self.copy_rename(rf'sol/{self.id}\.({self._prog_ext})', rf'prog/{self.id}.\1'), 'No model solution')
        for i, p in enumerate(self.find(rf'sol/{self.id}.+\.{self._prog_ext}')):
            self.copy(p, lambda p: re.sub(rf'.*\.({self._prog_ext})', rf'prog/{self.id}{i + 2}.\1', p))

        # Utils for reference
        self.copy(rf'utils/.*\.({self._prog_ext}|sh)', lambda p: f'prog/{p}')

    def make_checker(self):
        if self.find('check/standard_compare.cpp'):
            self.ignore('check/standard_compare.cpp')
        else:
            error_assert(self.copy_rename(rf'check/.*\.({self._prog_ext})', rf'prog/{self.id}chk.\1.todo'),
                              'Exactly one checker expected')

    def convert(self):
        self.make_tests()
        self.make_solutions()
        self.make_doc()
        self.make_checker()
        self.ignore('.sowa-sign')
        self.ignore('utils/.*')
        self.ignore('Makefile.in')
        self.ignore(f'info/{self.id}_opr.pdf')

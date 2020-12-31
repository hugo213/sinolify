import re

from sinolify.converter.base import ConverterBase
from sinolify.log import log, warning_assert, error_assert


class SowaToSinolConverter(ConverterBase):
    """ A converter used to convert Sowa packages to Sinol packages.

    See /dev/null for Sowa format specification and /dev/null for Sinol format specification.
    """

    _prog_ext = '(?:cpp|c|cc|pas)'

    @property
    def _id(self) -> str:
        """ A helper extracting source package ID. """
        return self._source.id

    def _make_tests(self) -> None:
        """ Copies tests (in/*.in, out/*.out). """
        error_assert(self.copy(rf'in/{self._id}\d+[a-z]*.in') > 0,
                     'No input files')
        warning_assert(self.copy(rf'out/{self._id}\d+[a-z]*.out') > 0,
                       'No output files')

    def _make_doc(self):
        """ Copies documents.

        Extracts the statement and its source to doc, along with anything
        that might be some sort of dependency.
        """
        error_assert(self.copy_rename(rf'doc/{self._id}\.pdf', f'doc/{self._id}zad.pdf') > 0,
                     'No problem statement')
        warning_assert(self.copy_rename(rf'desc/{self._id}\.tex', f'doc/{self._id}zad.tex'),
                       'No statement source')
        self.ignore(f'desc/{self._id}_opr.tex')
        self.copy_rename(rf'desc/(.*\.(?:pdf|tex))', rf'doc/\1', ignore_processed=True)

    def _make_solutions(self) -> None:
        """ Copies solutions.

        Copies the main solution (i.e. named exactly {task id}).
        The remaining solutions are copied in unspecified order and are
        numbered with integers starting from 2.
        """
        log.debug('Making solutions')
        error_assert(self.copy_rename(rf'sol/{self._id}\.({self._prog_ext})', rf'prog/{self._id}.\1'), 'No model solution')
        for i, p in enumerate(self.find(rf'sol/{self._id}.+\.{self._prog_ext}')):
            self.copy(p, lambda p: re.sub(rf'.*\.({self._prog_ext})', rf'prog/{self._id}{i + 2}.\1', p))

        self.copy(rf'utils/.*\.({self._prog_ext}|sh)', lambda p: f'prog/{p}')

    def _make_checker(self) -> None:
        """Copies a checker.

        If a checker is named `standard_compare.cpp` it is assumed to be the
        default checker that can be safely ignored. Otherwise it is copied
        with `.todo` suffix and a warning is emmited, as Sowa checkers need
        manual fix to work.
        """
        if self.find('check/standard_compare.cpp'):
            self.ignore('check/standard_compare.cpp')
        else:
            error_assert(self.copy_rename(rf'check/.*\.({self._prog_ext})', rf'prog/{self._id}chk.\1.todo'),
                         'Exactly one checker expected')

    def convert(self) -> None:
        """ Executes a conversion from Sowa to Sinol.

        Emits a warning if some unexpected files are not processed.
        """
        self._make_tests()
        self._make_solutions()
        self._make_doc()
        self._make_checker()
        self.ignore('.sowa-sign')  #
        self.ignore('utils/.*')
        self.ignore('Makefile.in')
        self.ignore(f'info/{self._id}_opr.pdf')

        if self.not_processed():
            log.warning('%d file(s) not processed: %s', len(self.not_processed()),
                        ', '.join(self.not_processed()))

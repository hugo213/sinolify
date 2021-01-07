import re

from sinolify.converters.base import ConverterBase
from sinolify.utils.log import log, warning_assert, error_assert


class SowaToSinolConverter(ConverterBase):
    """ A converters used to convert Sowa packages to Sinol packages.

    See /dev/null for Sowa format specification and /dev/null for Sinol format
    specification.
    """

    _prog_ext = '(?:cpp|c|cc|pas)'

    @property
    def _id(self) -> str:
        """ A helper extracting source package ID. """
        return self._source.id

    def _make_tests(self) -> None:
        """ Copies tests. """
        error_assert(self.copy(rf'in/{self._id}\d+[a-z]*.in') > 0,
                     'No input files')
        warning_assert(self.copy(rf'out/{self._id}\d+[a-z]*.out') > 0,
                       'No output files')

    def _make_doc(self):
        """ Copies documents.

        Extracts the statement and its source to doc, along with anything
        that might be some sort of dependency.
        """
        error_assert(self.copy_rename(rf'doc/{self._id}\.pdf',
                                      f'doc/{self._id}zad.pdf') > 0,
                     'No problem statement')
        warning_assert(self.copy_rename(rf'desc/{self._id}\.tex',
                                        f'doc/{self._id}zad.tex'),
                       'No statement source')
        self.ignore(f'desc/{self._id}_opr.tex')
        self.copy_rename(rf'desc/(.*\.(?:pdf|tex|cls|png|jpg|JPG|sty|odg))', rf'doc/\1',
                         ignore_processed=True)

    def _make_solutions(self) -> None:
        """ Copies solutions.

        Copies the main solution (i.e. named exactly {task id}).
        The remaining solutions are copied in unspecified order and are
        numbered with integers starting from 2.
        """
        log.debug('Making solutions')

        error_assert(self.copy_rename(rf'sol/{self._id}\.({self._prog_ext})',
                                      rf'prog/{self._id}.\1'),
                     'No main model solution')

        for i, p in enumerate(self.find(rf'sol/{self._id}.+\.{self._prog_ext}')):
            self.copy(p, lambda p: re.sub(rf'.*\.({self._prog_ext})',
                                          rf'prog/{self._id}{i + 2}.\1', p))

        self.copy(rf'utils/.*\.({self._prog_ext}|sh)', lambda p: f'prog/{p}')
        self.copy_rename(rf'sol/(.*{self._prog_ext})', r'prog/other/\1')

    def _make_checker(self) -> None:
        """Copies a checker.

        If a checker is named `standard_compare.cpp` it is assumed to be the
        default checker that can be safely ignored. Otherwise it is copied
        with `.todo` suffix and a warning is emmited, as Sowa checkers need
        manual fix to work.
        """
        if not self.exists('check/.*'):
            log.debug('No checker found')
        elif self.exists('check/standard_compare.cpp'):
            log.debug('Standard checker found')
            self.ignore('check/standard_compare.cpp')
        else:
            error_assert(self.copy_rename(rf'check/.*\.({self._prog_ext})',
                                          rf'prog/{self._id}chk.\1.todo') == 1,
                         'Exactly one checker expected')
            log.warning('Non-standard checker requires manual fix.')
        self.ignore('check/[^.]*')

    def convert(self) -> None:
        """ Executes a conversion from Sowa to Sinol.

        Emits a warning if some unexpected files are not processed.
        """
        self._make_tests()
        self._make_solutions()
        self._make_doc()
        self._make_checker()

        # Ignore ditor backup files
        self.ignore(r'.*(~|\.swp|\.backup|\.bak)')

        # Ignore package creation system files
        self.ignore(r'.sowa-sign')
        self.ignore(r'(.*/)?Makefile(\.in)?')

        # Ignore utils
        self.ignore(r'utils/.*')

        # Ignore LaTeX's leftovers
        self.ignore(r'desc/.*\.(aux|log|synctex)')

        # Ignore solution description
        self.ignore(f'info/{self._id}_opr.pdf')

        # Ignore some common temporary files left by authors
        self.ignore(r'tmpdesc/.*')
        self.ignore(r'(sol|check)/.*(\.o|_PAS|_CPP|_C|\.out)')
        self.ignore(rf'[^/]*\.{self._prog_ext}')

        if self.not_processed():
            log.warning('%d file(s) not processed: %s', len(self.not_processed()),
                        ', '.join(self.not_processed()))

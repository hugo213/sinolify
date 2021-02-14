import os
import re
import shutil

from sinolify.converters.base import ConverterBase
from sinolify.converters.mapping import ConversionMapping
from sinolify.utils.log import log, warning_assert, error_assert, die
from sinolify.heuristics.limits import pick_time_limits


class SowaToSinolConverter(ConverterBase):
    """ A converter used to convert Sowa packages to Sinol packages.

    See /dev/null for Sowa format specification and /dev/null for Sinol format
    specification.
    """

    _prog_ext = '(?:cpp|c|cc|pas)'

    def __init__(self, *args, auto_time_limits=True, threads=1, checkers=None, **kwargs):
        """ Instantiates new SowaToSinolConverter.

        :param auto_time_limits: If true, automatically sets time limits.
        :param threads: Number of threads for parallel execution.
        """
        super().__init__(*args, **kwargs)
        self.auto_time_limits = auto_time_limits
        self.threads = threads
        if checkers:
            checkers_find, checkers_replace = checkers
            log.info(f"Setting up checker mapping {checkers_find} -> {checkers_replace}")
            self.checkers_mapper = ConversionMapping(checkers_find, checkers_replace)
        else:
            self.checkers_mapper = None

    @property
    def _id(self) -> str:
        """ A helper extracting source package ID. """
        return self._source.id

    def make_tests(self) -> None:
        """ Copies tests. """
        error_assert(self.copy(rf'in/{self._id}\d+[a-z]*.in') > 0,
                     'No input files')
        warning_assert(self.copy(rf'out/{self._id}\d+[a-z]*.out') > 0,
                       'No output files')

    def make_doc(self):
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

    def make_solutions(self) -> None:
        """ Copies solutions.

        Copies the main solution (i.e. named exactly {task id}) to {task id}1.
        The remaining solutions are copied in unspecified order and are
        numbered with integers starting from 2.
        """
        log.debug('Making solutions')

        error_assert(self.copy_rename(rf'sol/{self._id}\.({self._prog_ext})',
                                      rf'prog/{self._id}1.\1'),
                     'No main model solution')

        for i, p in enumerate(self.find(rf'sol/{self._id}.+\.{self._prog_ext}')):
            self.copy(p, lambda p: re.sub(rf'.*\.({self._prog_ext})',
                                          rf'prog/{self._id}{i + 2}.\1', p))

        self.copy(rf'utils/.*\.({self._prog_ext}|sh)', lambda p: f'prog/{p}')
        self.copy_rename(rf'sol/(.*{self._prog_ext})', r'prog/other/\1', ignore_processed=True)

    def make_checker(self) -> None:
        """ Converts a checker.

        If no checker is found in check/, then no action is performed.
        Otherwise a checker is looked up in the checker mapper. If no
        match is found, checker is put in the mapper as `todo` and
        the program terminates with an error. Otherwise the mapped
        replacement is copied as package's checker.
        """

        original_checker = self.one(rf'check/.*\.{self._prog_ext}')
        if not original_checker:
            log.warning('No checker found.')
            return
        self.ignore(original_checker)
        original_checker = self._source.abspath(original_checker)
        error_assert(self.checkers_mapper, 'Checker found but no checker mapper was set up.')
        try:
            replacement = self.checkers_mapper.find(original_checker)
            if not replacement:
                log.info('Ignoring the checker.')
                return
            log.info(f'Copying the checker from mapper: {replacement}')
            shutil.copy(replacement, self._target.abspath(f'prog/{self._id}chk{os.path.splitext(replacement)[1]}'))
        except ConversionMapping.FindError:
            todo_filename = self.checkers_mapper.todo(original_checker)
            die(f'Putting the checker in mapper as {todo_filename}. Please fix it.')
        except ConversionMapping.ReplaceError:
            die('Unable to find a replacement for the checker in checker mapper.')
        self.ignore('check/[^.]*')

    def make_time_limits_config(self) -> str:
        """ Heuristically chooses time limit and returns config entry setting it """

        main_solution = self.one(rf'sol/{self._id}\.{self._prog_ext}')
        error_assert(main_solution, 'No main solution found')
        main_solution = self._source.abspath(main_solution)
        inputs = [self._source.abspath(p) for p in self.find(rf'in/{self._id}\d+[a-z]*.in')]
        limit = int(pick_time_limits(main_solution, inputs, threads=self.threads) * 1000)

        config = 'time_limits:\n'
        tests = [os.path.basename(i).lstrip(self._id).rstrip('.in') for i in inputs]
        config += '\n'.join([f'    {test}: {limit}' for test in sorted(tests)])
        return config

    def make_title_config(self):
        """ Extracts title from LaTeX and outputs config entry. """
        statement = self.one(rf'desc/{self._id}\.tex')
        if not statement:
            log.warning('Title requires manual setting.')
            return "title: TODO\n"
        else:
            latex = open(self._source.abspath(statement)).read()
            title = re.search(r'\\title{(?:\\mbox{)?([^}]*)}', latex).group(1).replace('~', ' ')
            return f'title: {title}\n'

    def make_config(self):
        """ Generates Sinol config. """
        config = open(self._target.abspath('config.yml'), 'w')
        config.write(self.make_title_config())
        if self.auto_time_limits:
            config.write(self.make_time_limits_config())

    def convert(self) -> None:
        """ Executes a conversion from Sowa to Sinol.

        Emits a warning if some unexpected files are not processed.
        """
        self.make_tests()
        self.make_solutions()
        self.make_doc()
        self.make_checker()
        self.make_config()

        # Ignore editor backup files
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

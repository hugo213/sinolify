import os
import subprocess
from typing import Optional, List


class CompilerBase(object):
    """ Base class for a compiler. """

    supported_extensions: List[str] = []
    default_flags: List[str] = []

    def __init__(self, src_path: str, *, output_ext: str = '.e',
                 flags: Optional[str] = None, timeout: int = 10):
        """ Instantiates a new compiler.

        :param src_path: Source file to compile.

        :param output_ext: Extension for output file.

        :param flags: Overrides default compiler flags.

        :param timeout: Timeout for compilation to complete.
        """
        src_path = os.path.abspath(src_path)
        src_path_without_ext, src_ext = os.path.splitext(src_path)
        assert src_ext in self.supported_extensions
        self.src_path = src_path
        self.flags = self.default_flags if flags is None else flags
        self.timeout = timeout
        self.exe_path = src_path_without_ext + output_ext
        self.log = ''

    def cmd(self) -> str:
        """ Returns command to compile the code. """
        raise NotImplementedError

    def compile(self) -> bool:
        """ Runs compile command (`cmd()`) and sets `log`.

        :return: True on success
        """
        try:
            self.log = subprocess.check_output(self.cmd(), stderr=subprocess.STDOUT,
                                               timeout=self.timeout).decode('utf-8')
            return True
        except subprocess.CalledProcessError as e:
            self.log = e.output.decode('utf-8')
            return False


class CppCompiler(CompilerBase):
    supported_extensions = ['.cc', '.cpp']
    default_flags = ['-O3', '--static', '--std=c++17']

    def cmd(self) -> bool:
        return ['g++'] + self.flags + [f'-o{self.exe_path}', f'{self.src_path}']


class PascalCompiler(CompilerBase):
    supported_extensions = ['.pas']
    default_flags = ['-O3']

    def cmd(self) -> bool:
        return ['pc'] + self.flags + [f'-o{self.exe_path}', f'{self.src_path}']


def compiler(path, **kwargs):
    """ Selects and instantiates a compiler for a given path."""
    ext = os.path.splitext(path)[1]
    for c in CompilerBase.__subclasses__():
        if ext in c.supported_extensions:
            return c(path, **kwargs)
    raise LookupError(f'Unknown source code extension {ext}')
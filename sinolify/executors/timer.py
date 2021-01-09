import subprocess
import tempfile
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Iterable
import re

from sinolify.utils.system import where


class TimerBase:
    def __init__(self, exe_file):
        self.exe_file = exe_file

    def measure(self, input_file: str) -> float:
        raise NotImplementedError


class PerfTimer(TimerBase):
    def __init__(self, exe_file, timeout=30, ghz=2):
        super().__init__(exe_file)
        self.timeout = timeout
        self.ghz = ghz

    def measure(self, input_file: str) -> float:
        with tempfile.NamedTemporaryFile(mode='w') as tmp:
            subprocess.check_output(
                [where('perf'), 'stat', '-einstructions', '-x,', f'-o{tmp.name}', self.exe_file],
                stdin=open(input_file, 'r'), timeout=self.timeout)
            perf_out = open(tmp.name, 'r').read()
            instr = int(re.search(r'(\d+),,instructions', perf_out).group(1))
            return instr/(self.ghz*10**9)


class TimerPool:
    timer: TimerBase
    threads: int

    def __init__(self, timer, *, threads=1):
        self.timer = timer
        self.threads = threads

    def measure(self, input_files: Iterable[str]):
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = []
            for input_file in input_files:
                futures.append(executor.submit(self.timer.measure, input_file))
            return [f.result() for f in futures]

import math
import shutil
import tempfile
import os.path

from sinolify.executors.compilers import compiler
from sinolify.executors.timer import TimerPool, PerfTimer
from sinolify.utils.log import error_assert, log


def pick_time_limits(src_file, input_files, *, threads=1):
    log.info(f'Picking time limits for {src_file}')
    with tempfile.TemporaryDirectory() as sandbox:
        src_ext = os.path.splitext(src_file)[1]
        sandboxed_src = os.path.join(sandbox, f'a{src_ext}')
        shutil.copy(src_file, sandboxed_src)
        c = compiler(sandboxed_src, output_ext='.e')
        error_assert(c.compile(), f'Failed to compile the solution:\n{c.log}')
        sandboxed_exe = os.path.join(sandbox, 'a.e')
        times = TimerPool(PerfTimer(sandboxed_exe, timeout=20), threads=threads).measure(input_files)
        max_time = max(times)
        limit = 3 * max_time
        return math.ceil(2*limit)/2
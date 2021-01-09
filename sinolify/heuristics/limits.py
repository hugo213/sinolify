import math
import shutil
import tempfile
import os.path

from sinolify.executors.compilers import compiler
from sinolify.executors.timer import TimerPool, PerfTimer
from sinolify.utils.log import log, die


def pick_time_limits(src_file, input_files, *, threads=1):
    """ Heuristically picks time limits based on solution's performance.

    The solution is compiled and run on all input files.
    Maximum time is multiplied by 3 and rounded up to a multiply of 0.5s.

    :param src_file: Solution source file.

    :param input_files: Input files to test solution on.

    :param threads: Number of parallel runs allowed.

    :returns: Suggested time limit.
    """
    log.info(f'Picking time limits for {src_file}')
    with tempfile.TemporaryDirectory() as sandbox:
        src_ext = os.path.splitext(src_file)[1]
        sandboxed_src = os.path.join(sandbox, f'a{src_ext}')
        shutil.copy(src_file, sandboxed_src)
        c = compiler(sandboxed_src, output_ext='.e')
        if not c.compile():
            log.info(c.log)
            die('Failed to compile model solution')
        log.debug(c.log)
        sandboxed_exe = os.path.join(sandbox, 'a.e')
        times = TimerPool(PerfTimer(sandboxed_exe, timeout=20), threads=threads).measure(input_files)
        max_time = max(times)
        limit = 3 * max_time
        return math.ceil(2*limit)/2
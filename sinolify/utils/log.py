import logging
import sys

log = logging.getLogger(__package__)
log.addHandler(logging.StreamHandler(stream=sys.stderr))


def warning_assert(condition, *args):
    if not condition:
        log.warning(*args)


def error_assert(condition, *args):
    if not condition:
        log.error(*args)
        exit(1)
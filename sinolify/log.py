import logging
log = logging.getLogger(__package__)


def warning_assert(condition, *args):
    if not condition:
        log.warning(*args)


def error_assert(condition, *args):
    if not condition:
        log.error(*args)
        exit(1)
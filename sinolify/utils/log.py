import logging
import sys

log = logging.getLogger(__package__)
_handler = logging.StreamHandler(stream=sys.stderr)
_handler.setFormatter(logging.Formatter('%(levelname)-7s %(message)s'))
log.addHandler(_handler)


def die(*args):
    log.error(*args)
    exit(1)


def warning_assert(condition, *args):
    if not condition:
        log.warning(*args)


def error_assert(condition, *args):
    if not condition:
        die(*args)
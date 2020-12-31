import argparse
import logging

from sinolify.utils.log import log


class ToolBase:
    description = 'CLI Tool Base'

    _loglevels = {
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }

    def make_parser(self):
        parser = argparse.ArgumentParser(description=self.description)
        parser.add_argument('-v', choices=self._loglevels, default='warning', help='Verbosity level')
        return parser

    def setup_logging(self, level):
        log.setLevel(level)

    def validate_args(self, args):
        pass

    def main(self):
        raise NotImplementedError

    def __init__(self, argv):
        self.args = self.make_parser().parse_args(argv)
        self.validate_args(self.args)
        self.setup_logging(self._loglevels[self.args.v])
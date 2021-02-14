import os.path
import sys

from sinolify.utils.package import Package
from sinolify.converters.sowa import SowaToSinolConverter
from sinolify.utils.log import log, error_assert
from sinolify.tools.base import ToolBase


class ConvertTool(ToolBase):
    description = 'Sowa to Sinol converter.'

    def make_parser(self):
        parser = super().make_parser()

        parser.add_argument('source', type=str,
                            help='Sowa .zip package path')

        parser.add_argument('output', type=str,
                            help='Output .zip file path')

        parser.add_argument('-f', '--force', action='store_true',
                            help='Allow overwrite of output file')

        parser.add_argument('--time', action='store_true',
                            help='Auto adjust time limits')

        parser.add_argument('--checkers', type=str,
                            help='Checker mapping directory')

        parser.add_argument('--dry', action='store_true',
                            help='Dry run, do not save the result')

        parser.add_argument('-j', '--threads', type=int, default=1,
                            help='Number of threads for adjusting time limits')
        return parser

    def validate_args(self, args):
        error_assert(args.output.endswith('.zip'), 'Output must end with .zip')
        error_assert(args.force or not os.path.exists(args.output), 'Output exists. Use -f to overwrite.')
        error_assert(not args.checkers or os.path.exists(args.checkers), 'Checker mapping directory does not exist.')
        error_assert(not args.checkers or (os.path.isdir(os.path.join(args.checkers, 'find'))
                     and os.path.isdir(os.path.join(args.checkers, 'replace'))),
                     'Checker mapping directory must contain find/ and replace/ subdirectories.')

    def main(self):
        sowa = Package(zip=self.args.source)
        sinol = Package(id=sowa.id)
        if self.args.checkers:
            checkers = (os.path.join(self.args.checkers, 'find'), os.path.join(self.args.checkers, 'replace'))
        else:
            checkers = None
        converter = SowaToSinolConverter(sowa, sinol, auto_time_limits=self.args.time, threads=self.args.threads,
                                         checkers=checkers)
        converter.convert()
        if not self.args.dry:
            sinol.save(self.args.output, overwrite=self.args.force)
            log.info('Output saved to %s', self.args.output)


def main():
    ConvertTool(sys.argv[1:]).main()


if __name__ == '__main__':
    main()

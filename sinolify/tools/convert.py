import os.path
import sys

from sinolify.utils.package import Package
from sinolify.converters.sowa import SowaToSinolConverter
from sinolify.utils.log import log
from sinolify.tools.base import ToolBase


class ConvertTool(ToolBase):
    description = 'Sowa to Sinol converters'

    def make_parser(self):
        parser = super().make_parser()

        parser.add_argument('source', type=str,
                            help='Sowa .zip package path')

        parser.add_argument('output', type=str,
                            help='Output .zip file path')

        parser.add_argument('-f', action='store_true',
                            help='Allow overwrite of output file')

        parser.add_argument('-t', action='store_true',
                            help='Auto adjust time limits')

        parser.add_argument('-j', type=int, default=1,
                            help='Number of threads for adjusting time limits')
        return parser

    def validate_args(self, args):
        assert args.output.endswith('.zip'), 'Output must end with .zip'
        assert args.f or not os.path.exists(args.output), 'Output exists. Use -f to overwrite.'

    def main(self):
        sowa = Package(zip=self.args.source)
        sinol = Package(id=sowa.id)
        converter = SowaToSinolConverter(sowa, sinol, auto_time_limits=self.args.t, threads=self.args.j)
        converter.convert()
        sinol.save(self.args.output, overwrite=self.args.f)
        log.info('Output saved to %s', self.args.output)


def main():
    ConvertTool(sys.argv[1:]).main()


if __name__ == '__main__':
    main()

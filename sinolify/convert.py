import argparse
import logging
import sys
import os.path

from sinolify.package import Package
from sinolify.converter.sowa import SowaToSinolConverter
from sinolify.log import log

def main():
    parser = argparse.ArgumentParser(description='Sowa -> Sinol converter')
    parser.add_argument('source', type=str, help='Sowa .zip package path')
    parser.add_argument('output', type=str, help='Output .zip file path')
    parser.add_argument('-f', action='store_true', help='Allow overwrite of output file')
    loglevels = {'error': logging.ERROR, 'warning': logging.WARNING, 'info': logging.INFO, 'debug': logging.DEBUG}
    parser.add_argument('-v', choices=loglevels, default='warning', help='Verbosity level')
    args = parser.parse_args()

    assert args.output.endswith('.zip'), 'Output must end with .zip'
    assert args.f or not os.path.exists(args.output), 'Output exists. Use -f to overwrite.'
    log.setLevel(loglevels[args.v])
    log.addHandler(logging.StreamHandler(stream=sys.stderr))

    sowa = Package(zip=args.source)
    sinol = Package(id=sowa.id)
    converter = SowaToSinolConverter(sowa, sinol)
    converter.convert()

    sinol.save(args.output, overwrite=args.f)
    log.info('Output saved to %s', args.output)


if __name__ == '__main__':
    main()
"""
Command-line script to convert a .gctx file to .gct. 

Main method takes in a .gctx file path (and, optionally, an 
	out path and/or name to which to save the equivalent .gctx)
	and saves the enclosed content to a .gct file. 

Note: Only supports v1.0 .gctx files. 
"""

import logging
from . import setup_GCToo_logger as setup_logger
import argparse
import sys
from . import parse_gctx
from . import write_gct
import os.path

__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # required
    parser.add_argument("-filename", "-f",
                        help=".gctx file that you would like converted to .gct form", required=True)
    # optional
    parser.add_argument("-output_filepath",
                        help="(optional) out path/name for output gctx file.  Default will be the same as input but with extension changed from gctx to gct",
                        default=None)
    parser.add_argument("-verbose", "-v",
                        help="Whether to print a bunch of output.", action="store_true", default=False)
    return parser


def main():
    args = build_parser().parse_args(sys.argv[1:])
    setup_logger.setup(verbose=args.verbose)
    in_gctoo = parse_gctx.parse(args.filename, convert_neg_666=False)
    if args.output_filepath == None:
        basename = os.path.basename(args.filename)
        out_name = ".".join(basename.split(".")[:-1])
    else:
        out_name = args.output_filepath

    write_gct.write(in_gctoo, out_name)


if __name__ == "__main__":
    main()

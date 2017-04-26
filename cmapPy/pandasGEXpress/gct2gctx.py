"""
Command-line script to convert a .gct file to .gctx. 

Main method takes in a .gct file path (and, optionally, an 
	out path and/or name to which to save the equivalent .gctx)
	and saves the enclosed content to a .gctx file. 

Note: Only supports v1.3 .gct files. 
"""

import logging
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger
import argparse
import sys
import GCToo
import parse_gct
import write_gctx

__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)


def build_parser():
	parser = argparse.ArgumentParser(description=__doc__, 
		formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	# required
	parser.add_argument("-filename", 
		help=".gct file that you would like converted to .gctx form")
	# optional
	parser.add_argument("-output_filepath", 
		help="(optional) out path/name for output gctx file", default=None)
	parser.add_argument("-verbose", "-v", 
		help="Whether to print a bunch of output.", action="store_true", default=False)
	return parser

def main():
	args = build_parser().parse_args(sys.argv[1:])
	setup_logger.setup(verbose=args.verbose)
	in_gctoo = parse_gct.parse(args.filename, convert_neg_666=False)
	logger.debug("Original out name: {}".format(in_gctoo.src))

	if args.output_filepath == None:
		out_name = str.split(in_gctoo.src, "/")[-1].split(".")[0]
	else:
		out_name = args.output_filepath

	write_gctx.write(in_gctoo, out_name)


if __name__ == "__main__":
	main()
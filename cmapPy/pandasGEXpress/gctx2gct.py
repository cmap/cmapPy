"""
Command-line script to convert a .gctx file to .gct. 

Main method takes in a .gctx file path (and, optionally, an 
	out path and/or name to which to save the equivalent .gct)
	and saves the enclosed content to a .gct file. 

Note: Only supports v1.0 .gctx files. 
"""
import sys
import logging
import argparse
import os.path
import pandas as pd
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.parse_gctx as parse_gctx
import cmapPy.pandasGEXpress.write_gct as write_gct

__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # required
    parser.add_argument("-filename", "-f", required=True,
                        help=".gctx file that you would like to converted to .gct")
    # optional
    parser.add_argument("-output_filepath", "-o", default=None,
                        help=("out path/name for output gct file. " +
                              "Default is just to modify the extension"))
    parser.add_argument("-verbose", "-v",
                        help="Whether to print a bunch of output.", action="store_true", default=False)
    parser.add_argument("-row_annot_path", help="Path to annotations file for rows")
    parser.add_argument("-col_annot_path", help="Path to annotations file for columns")
    return parser


def main():
    args = build_parser().parse_args(sys.argv[1:])
    setup_logger.setup(verbose=args.verbose)
    gctx2gct_main(args)


def gctx2gct_main(args):
    """ Separate from main() in order to make command-line tool. """

    in_gctoo = parse_gctx.parse(args.filename, convert_neg_666=False)

    if args.output_filepath is None:
        basename = os.path.basename(args.filename)
        out_name = os.path.splitext(basename)[0] + ".gct"
    else:
        out_name = args.output_filepath

    """ If annotations are supplied, parse table and set metadata_df """
    if args.row_annot_path is None:
        pass
    else:
        row_metadata = pd.read_csv(args.row_annot_path, sep='\t', index_col=0, header=0, low_memory=False)
        assert all(in_gctoo.data_df.index.isin(row_metadata.index)), \
            "Row ids in matrix missing from annotations file"
        in_gctoo.row_metadata_df = row_metadata.loc[row_metadata.index.isin(in_gctoo.data_df.index)]

    if args.col_annot_path is None:
        pass
    else:
        col_metadata = pd.read_csv(args.col_annot_path, sep='\t', index_col=0, header=0, low_memory=False)
        assert all(in_gctoo.data_df.columns.isin(col_metadata.index)), \
            "Column ids in matrix missing from annotations file"
        in_gctoo.col_metadata_df = col_metadata.loc[col_metadata.index.isin(in_gctoo.data_df.columns)]

    write_gct.write(in_gctoo, out_name)


if __name__ == "__main__":
    main()

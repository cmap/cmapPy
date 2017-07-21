"""
slice_gct.py

Extract a subset of data from a gct file. If called from the command line,
ids can be provided as a list or as a path to a grp file. If using the
slice method in Python, ids or boolean arrays can be used.

"""

import logging
import sys
import os
import argparse
import pandas as pd
import re

import setup_GCToo_logger as setup_logger
import GCToo 
import parse_gct as pg
import write_gct as wg

__author__ = "Lev Litichevskiy"
__email__ = "lev@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)


def build_parser():
    """Build argument parser."""

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required args
    parser.add_argument("--in_gct_path", "-i", required=True, help="file path to input gct file")

    parser.add_argument("--rid", nargs="+", help="filepath to grp file or string array for including rows")
    parser.add_argument("--cid", nargs="+", help="filepath to grp file or string array for including cols")
    parser.add_argument("--exclude_rid", "-er", nargs="+", help="filepath to grp file or string array for excluding rows")
    parser.add_argument("--exclude_cid", "-ec", nargs="+", help="filepath to grp file or string array for excluding cols")
    parser.add_argument("--out_name", "-o", default="ds_sliced.gct",
                        help="what to name the output file")
    parser.add_argument("--verbose", "-v", action="store_true", default=False,
                        help="whether to increase the # of messages reported")

    return parser


def main():
    # get args
    args = build_parser().parse_args(sys.argv[1:])
    setup_logger.setup(verbose=args.verbose)

    # Read the input gct
    in_gct = pg.parse(args.in_gct_path)

    # Read in each of the command line arguments
    rid = _read_arg(args.rid)
    cid = _read_arg(args.cid)
    exclude_rid = _read_arg(args.exclude_rid)
    exclude_cid = _read_arg(args.exclude_cid)

    # Slice the gct
    out_gct = slice_gctoo(in_gct, rid=rid, cid=cid, exclude_rid=exclude_rid, exclude_cid=exclude_cid)
    assert out_gct.data_df.size > 0, "Slicing yielded an empty gct!"

    # Write the output gct
    wg.write(out_gct, args.out_name, data_null="NaN", metadata_null="NA", filler_null="NA")


def read_grp(in_path):
    """ Read .grp file to a list. """

    with open(in_path, 'r') as f:
            lines = f.readlines()
            # second conditional ignores comment lines
            return [line.strip() for line in lines if line and not re.match('^#', line)]


def _read_arg(arg):
    """
    If arg is a list with 1 element that corresponds to a valid file path, use
    plategrp to read the grp file. Otherwise, check that arg is a list of strings.

    Args:
        arg (list or None)

    Returns:
        arg_out (list or None)
    """

    # If arg is None, just return it back
    if arg is None:
        arg_out = arg

    else:
        # If len(arg) == 1 and arg[0] is a valid filepath, read it as a grp file
        if len(arg) == 1 and os.path.exists(arg[0]):
            arg_out = read_grp(arg[0])
        else:
            arg_out = arg

        # Make sure that arg_out is a list of strings
        assert isinstance(arg_out, list), "arg_out must be a list."
        assert type(arg_out[0]) == str, "arg_out must be a list of strings."

    return arg_out


def slice_gctoo(gctoo, row_bool=None, col_bool=None, rid=None, cid=None, exclude_rid=None, exclude_cid=None):
    """ Extract a subset of data from a GCToo object in a variety of ways.

    Args:
        gctoo (GCToo object)
        row_bool (list of bools): length must equal gctoo.data_df.shape[0]
        col_bool (list of bools): length must equal gctoo.data_df.shape[1]
        rid (list of strings): length must equal gctoo.data_df.shape[0]
        cid (list of strings): length must equal gctoo.data_df.shape[0]
        exclude_rid (bool): if true, select row ids EXCLUDING 'rid' (default: False)
        exclude_cid (bool): if true, select col ids EXCLUDING 'cid' (default: False)

    Returns:
        out_gctoo (GCToo object): gctoo after slicing
    """
    assert (rid is None) or (row_bool is None), (
        "rid and row_bool should not BOTH be provided.")
    assert (cid is None) or (col_bool is None), (
        "cid and col_bool should not BOTH be provided.")

    ### ROWS
    # Use rid if provided
    if rid is not None:
        rows_to_keep = [gctoo_row for gctoo_row in gctoo.data_df.index if gctoo_row in rid]

    else:
        # Use row_bool if provided
        if row_bool is not None:

            assert len(row_bool) == gctoo.data_df.shape[0], (
                "row_bool must have length equal to gctoo.data_df.shape[0]. " +
                "len(row_bool): {}, gctoo.data_df.shape[0]: {}".format(
                    len(row_bool), gctoo.data_df.shape[0]))
            rows_to_keep = gctoo.data_df.index[row_bool].values

        else:
            # If rid and row_bool are both None, return all rows
            rows_to_keep = gctoo.data_df.index.values

    # Use exclude_rid if provided
    if exclude_rid is not None:
        # Keep only those rows that are not in exclude_rid
        rows_to_keep = [row_to_keep for row_to_keep in rows_to_keep if row_to_keep not in exclude_rid]

    ### COLUMNS
    # Use cid if provided
    if cid is not None:
        cid = pd.Series(cid)
        cols_to_keep = cid[cid.isin(gctoo.data_df.columns)]
    else:
        # Use col_bool if provided
        if col_bool is not None:

            assert len(col_bool) == gctoo.data_df.shape[1], (
                "col_bool must have length equal to gctoo.data_df.shape[1]. " +
                "len(col_bool): {}, gctoo.data_df.shape[1]: {}".format(
                    len(col_bool), gctoo.data_df.shape[1]))
            cols_to_keep = gctoo.data_df.columns[col_bool].values

        else:
            # If cid and col_bool are both None, return all cols
            cols_to_keep = gctoo.data_df.columns.values

    # Use exclude_cid if provided
    if exclude_cid is not None:
        # Keep only those cols that are not in exclude_cid
        cols_to_keep = [col_to_keep for col_to_keep in cols_to_keep if col_to_keep not in exclude_cid]

    # Convert labels to boolean array
    rows_to_keep_bools = gctoo.data_df.index.isin(rows_to_keep)
    cols_to_keep_bools = gctoo.data_df.columns.isin(cols_to_keep)

    # Make the output gct
    out_gctoo = GCToo.GCToo(
        src= gctoo.src, version = gctoo.version,
        data_df=gctoo.data_df.loc[rows_to_keep_bools, cols_to_keep_bools],
        row_metadata_df=gctoo.row_metadata_df.loc[rows_to_keep_bools, :],
        col_metadata_df=gctoo.col_metadata_df.loc[cols_to_keep_bools, :])

    return out_gctoo


if __name__ == "__main__":
    main()
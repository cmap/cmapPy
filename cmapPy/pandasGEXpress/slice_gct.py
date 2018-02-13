"""
slice_gct.py

Extract a subset of data from a GCT(x) file using the command line. ids can
be provided as a list or as a path to a grp file. See slice_gctoo for the
equivalent method to be used on GCToo objects.

"""
import logging
import sys
import os
import argparse

import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.parse as parse
import cmapPy.pandasGEXpress.slice_gctoo as sg
import cmapPy.pandasGEXpress.write_gct as wg
import cmapPy.pandasGEXpress.write_gct as wgx
import cmapPy.set_io.grp as grp

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
    parser.add_argument("--use_gctx", action="store_true", default=False,
                        help="whether to write output as GCTx")
    parser.add_argument("--verbose", "-v", action="store_true", default=False,
                        help="whether to increase the # of messages reported")

    return parser


def main():
    # Get args
    args = build_parser().parse_args(sys.argv[1:])
    setup_logger.setup(verbose=args.verbose)

    # Read the input gct
    in_gct = parse.parse(args.in_gct_path)

    # Read in each of the command line arguments
    rid = _read_arg(args.rid)
    cid = _read_arg(args.cid)
    exclude_rid = _read_arg(args.exclude_rid)
    exclude_cid = _read_arg(args.exclude_cid)

    # Slice the gct
    out_gct = sg.slice_gctoo(in_gct, rid=rid, cid=cid, exclude_rid=exclude_rid, exclude_cid=exclude_cid)
    assert out_gct.data_df.size > 0, "Slicing yielded an empty gct!"

    # Write the output gct
    if args.use_gctx:
        wgx.write(out_gct, args.out_name)
    else:
        wg.write(out_gct, args.out_name, data_null="NaN", metadata_null="NA", filler_null="NA")


def _read_arg(arg):
    """
    If arg is a list with 1 element that corresponds to a valid file path, use
    set_io.grp to read the grp file. Otherwise, check that arg is a list of strings.

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
            arg_out = grp.read(arg[0])
        else:
            arg_out = arg

        # Make sure that arg_out is a list of strings
        assert isinstance(arg_out, list), "arg_out must be a list."
        assert type(arg_out[0]) == str, "arg_out must be a list of strings."

    return arg_out


if __name__ == "__main__":
    main()

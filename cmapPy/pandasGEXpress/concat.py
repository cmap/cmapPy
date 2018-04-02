"""
concat.py

This function is for concatenating gct(x) files together. You can tell it to
find files using the file_wildcard argument, or you can tell it exactly
which files you want to concatenate using the input_filepaths argument. The
meat of this function are the hstack (i.e. horizontal concatenation of GCToo objects)
and vstack (i.e. vertical concatenation).

Terminology: 'Common' metadata refers to the metadata that is shared between
the loaded GCToo's. For example, if horizontally concatenating, the 'common' metadata is
the row metadata. 'Concatenated' metadata is the other one; it's the metadata
for the entries being concatenated together. For example, if horizontally
concatenating, the 'concatenated' metadata is the column metadata because
columns are being concatenated together.

There are 2 arguments that allow you to work around certain obstacles
of concatenation.

1) If the 'common' metadata contains fields that are not the same in
all files, then you will need to remove these fields using the
fields_to_remove argument.

2) If the 'concatenated' metadata ids are not unique between different files,
and you try to concatenate the files, an invalid GCToo would be formed
(duplicate ids). To overcome this, use the reset_sample_ids argument. This will
move the 'new' metadata ids to a new metadata field and replace the original ids
with unique integers.

N.B. This script sorts everything!

"""
import argparse
import os
import sys
import glob
import logging
import numpy
import pandas as pd

import cmapPy.pandasGEXpress.GCToo as GCToo
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.parse as parse
import cmapPy.pandasGEXpress.write_gct as write_gct
import cmapPy.pandasGEXpress.write_gctx as write_gctx


__author__ = "Lev Litichevskiy"
__email__ = "lev@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)


def build_parser():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Required args
    parser.add_argument("--concat_direction", "-d", required=True,
                        choices=["horiz", "vert"],
                        help="which direction to concatenate")

    mutually_exclusive_group = parser.add_mutually_exclusive_group()
    mutually_exclusive_group.add_argument("--input_filepaths", "-if", nargs="+",
        help="full paths to gct(x) files to be concatenated")
    mutually_exclusive_group.add_argument("--file_wildcard", "-w", type=str,
        help=("wildcard specifying where files should be found " +
              "(make sure to surround in quotes if calling from command line!)"))

    parser.add_argument("--out_type", "-ot", default="gctx", choices=["gct", "gctx"],
                        help="whether to save output as a gct or gctx")
    parser.add_argument("--out_name", "-o", type=str, default="concated.gctx",
        help="what to name the output file")
    parser.add_argument("--fields_to_remove", "-ftr", nargs="+", default=[],
        help="fields to remove from the common metadata")
    parser.add_argument("--remove_all_metadata_fields", "-ramf", action="store_true", default=False,
                        help="remove all metadata fields during operation")
    parser.add_argument("--reset_ids", "-rsi", action="store_true", default=False,
        help="whether to reset ids (use this flag if ids are not unique)")

    parser.add_argument("-data_null", type=str, default="NaN",
        help="how to represent missing values in the data")
    parser.add_argument("-metadata_null", type=str, default="-666",
        help="how to represent missing values in the metadata")
    parser.add_argument("-filler_null", type=str, default="-666",
        help="what value to use for filling the top-left filler block if output is a .gct")
    parser.add_argument("-verbose", "-v", action="store_true", default=False,
        help="whether to print a bunch of output")

    parser.add_argument("--error_report_output_file", "-erof", type=str, default=None,
                        help="""destination file for writing out error report - currently information about inconsistent
                        metadata fields in the common dimension of the concat operation""")

    return parser


def main():
    # get args
    args = build_parser().parse_args(sys.argv[1:])
    setup_logger.setup(verbose=args.verbose)
    logger.debug("args:  {}".format(args))

    concat_main(args)


def concat_main(args):
    """ Separate method from main() in order to make testing easier and to
    enable command-line access. """

    # Get files directly
    if args.input_filepaths is not None:
        files = args.input_filepaths

    # Or find them
    else:
        files = get_file_list(args.file_wildcard)
        
        # No files found
        if len(files) == 0:
            msg = "No files were found. args.file_wildcard: {}".format(args.file_wildcard)
            logger.error(msg)
            raise Exception(msg)

    # Only 1 file found
    if len(files) == 1:
        logger.warning("Only 1 file found. No concatenation needs to be done, exiting")
        return

    # More than 1 file found
    else:
        # Parse each file and append to a list
        gctoos = []
        for f in files:
            gctoos.append(parse.parse(f))

        # Create concatenated gctoo object
        if args.concat_direction == "horiz":
            out_gctoo = hstack(gctoos, args.remove_all_metadata_fields, args.error_report_output_file,
                               args.fields_to_remove, args.reset_ids)

        elif args.concat_direction == "vert":
            out_gctoo = vstack(gctoos, args.remove_all_metadata_fields, args.error_report_output_file,
                               args.fields_to_remove, args.reset_ids)

    # Write out_gctoo to file
    logger.info("Writing to output file args.out_name:  {}".format(args.out_name))

    if args.out_type == "gctx":
        write_gctx.write(out_gctoo, args.out_name)

    elif args.out_type == "gct":
        write_gct.write(out_gctoo, args.out_name,
                          filler_null=args.filler_null,
                          metadata_null=args.metadata_null,
                          data_null=args.data_null)


def get_file_list(wildcard):
    """ Search for files to be concatenated. Currently very basic, but could
    expand to be more sophisticated.

    Args:
        wildcard (regular expression string)

    Returns:
        files (list of full file paths)

    """
    files = glob.glob(os.path.expanduser(wildcard))
    return files


def hstack(gctoos, remove_all_metadata_fields=False, error_report_file=None, fields_to_remove=[], reset_ids=False):
    """ Horizontally concatenate gctoos.

    Args:
        gctoos (list of gctoo objects)
        remove_all_metadata_fields (bool):  ignore/strip all common metadata when combining gctoos
        error_report_file (string):  path to write file containing error report indicating 
            problems that occurred during hstack, mainly for inconsistencies in common metadata
        fields_to_remove (list of strings): fields to be removed from the
            common metadata because they don't agree across files
        reset_ids (bool): set to True if sample ids are not unique

    Return:
        concated (gctoo object)
    """
    # Separate each gctoo into its component dfs
    row_meta_dfs = []
    col_meta_dfs = []
    data_dfs = []
    srcs = []
    for g in gctoos:
        row_meta_dfs.append(g.row_metadata_df)
        col_meta_dfs.append(g.col_metadata_df)
        data_dfs.append(g.data_df)
        srcs.append(g.src)

    logger.debug("shapes of row_meta_dfs:  {}".format([x.shape for x in row_meta_dfs]))

    # Concatenate row metadata
    all_row_metadata_df = assemble_common_meta(row_meta_dfs, fields_to_remove, srcs, remove_all_metadata_fields, error_report_file)

    # Concatenate col metadata
    all_col_metadata_df = assemble_concatenated_meta(col_meta_dfs, remove_all_metadata_fields)

    # Concatenate the data_dfs
    all_data_df = assemble_data(data_dfs, "horiz")

    # Make sure df shapes are correct
    assert all_data_df.shape[0] == all_row_metadata_df.shape[0], "Number of rows in metadata does not match number of rows in data - all_data_df.shape[0]:  {}  all_row_metadata_df.shape[0]:  {}".format(all_data_df.shape[0], all_row_metadata_df.shape[0])
    assert all_data_df.shape[1] == all_col_metadata_df.shape[0], "Number of columns in data does not match number of columns metadata - all_data_df.shape[1]:  {}  all_col_metadata_df.shape[0]:  {}".format(all_data_df.shape[1], all_col_metadata_df.shape[0])
    
    # If requested, reset sample ids to be unique integers and move old sample
    # ids into column metadata
    if reset_ids:
        do_reset_ids(all_col_metadata_df, all_data_df, "horiz")

    logger.info("Build GCToo of all...")
    concated = GCToo.GCToo(row_metadata_df=all_row_metadata_df,
                           col_metadata_df=all_col_metadata_df,
                           data_df=all_data_df)

    return concated


def vstack(gctoos, remove_all_metadata_fields=False, error_report_file=None, fields_to_remove=[], reset_ids=False):
    """ Vertically concatenate gctoos.

    Args:
        gctoos (list of gctoo objects)
        remove_all_metadata_fields (bool):  ignore/strip all common metadata when combining gctoos
        error_report_file (string):  path to write file containing error report indicating 
            problems that occurred during vstack, mainly for inconsistencies in common metadata
        fields_to_remove (list of strings): fields to be removed from the
            common metadata because they don't agree across files
        reset_ids (bool): set to True if row ids are not unique

    Return:
        concated (gctoo object)
    """
    # Separate each gctoo into its component dfs
    row_meta_dfs = []
    col_meta_dfs = []
    data_dfs = []
    srcs = []
    for g in gctoos:
        row_meta_dfs.append(g.row_metadata_df)
        col_meta_dfs.append(g.col_metadata_df)
        data_dfs.append(g.data_df)
        srcs.append(g.src)

    # Concatenate col metadata
    all_col_metadata_df = assemble_common_meta(col_meta_dfs, fields_to_remove, srcs, remove_all_metadata_fields, error_report_file)

    # Concatenate col metadata
    all_row_metadata_df = assemble_concatenated_meta(row_meta_dfs, remove_all_metadata_fields)

    # Concatenate the data_dfs
    all_data_df = assemble_data(data_dfs, "vert")

    # Make sure df shapes are correct
    assert all_data_df.shape[0] == all_row_metadata_df.shape[0], "Number of rows is incorrect."
    assert all_data_df.shape[1] == all_col_metadata_df.shape[0], "Number of columns is incorrect."

    # If requested, reset sample ids to be unique integers and move old sample
    # ids into column metadata
    if reset_ids:
        do_reset_ids(all_row_metadata_df, all_data_df, "vert")

    logger.info("Build GCToo of all...")
    concated = GCToo.GCToo(row_metadata_df=all_row_metadata_df,
                           col_metadata_df=all_col_metadata_df,
                           data_df=all_data_df)

    return concated


def assemble_common_meta(common_meta_dfs, fields_to_remove, sources, remove_all_metadata_fields, error_report_file):
    """ Assemble the common metadata dfs together. Both indices are sorted.
    Fields that are not in all the dfs are dropped.

    Args:
        common_meta_dfs (list of pandas dfs)
        fields_to_remove (list of strings): fields to be removed from the
            common metadata because they don't agree across files

    Returns:
        all_meta_df_sorted (pandas df)

    """
    all_meta_df, all_meta_df_with_dups = build_common_all_meta_df(common_meta_dfs, fields_to_remove, remove_all_metadata_fields)

    if not all_meta_df.index.is_unique:
        all_report_df = build_mismatched_common_meta_report([x.shape for x in common_meta_dfs],
            sources, all_meta_df, all_meta_df_with_dups)

        unique_duplicate_ids = all_report_df.index.unique()

        if error_report_file is not None:
            all_report_df.to_csv(error_report_file, sep="\t")

        msg = """There are inconsistencies in common_metadata_df between different files.  Try excluding metadata fields
using the fields_to_remove argument.  unique_duplicate_ids: {}
all_report_df:
{}""".format(unique_duplicate_ids, all_report_df)
        raise MismatchCommonMetadataConcatException(msg)

    # Finally, sort the index
    all_meta_df_sorted = all_meta_df.sort_index(axis=0)

    return all_meta_df_sorted


def build_common_all_meta_df(common_meta_dfs, fields_to_remove, remove_all_metadata_fields):
    """
    concatenate the entries in common_meta_dfs, removing columns selectively (fields_to_remove) or entirely (
        remove_all_metadata_fields=True; in this case, effectively just merges all the indexes in common_meta_dfs).

        Returns 2 dataframes (in a tuple):  the first has duplicates removed, the second does not.

    Args:
        common_meta_dfs: collection of pandas DataFrames containing the metadata in the "common" direction of the
            concatenation operation
        fields_to_remove: columns to be removed (if present) from the common_meta_dfs
        remove_all_metadata_fields: boolean indicating that all metadata fields should be removed from the
            common_meta_dfs; overrides fields_to_remove if present

    Returns:
        tuple containing
            all_meta_df:  pandas dataframe that is the concatenation of the dataframes in common_meta_dfs,
            all_meta_df_with_dups:
    """

    if remove_all_metadata_fields:
        trimmed_common_meta_dfs = [pd.DataFrame(index=df.index) for df in common_meta_dfs]
    else:
        shared_column_headers = sorted(set.intersection(*[set(df.columns) for df in common_meta_dfs]))
        logger.debug("shared_column_headers:  {}".format(shared_column_headers))

        trimmed_common_meta_dfs = [df[shared_column_headers] for df in common_meta_dfs]

        # Remove any column headers that will prevent dfs from being identical
        for df in trimmed_common_meta_dfs:
            df.drop(fields_to_remove, axis=1, errors="ignore", inplace=True)

    # Concatenate all dfs and then remove duplicate rows
    all_meta_df_with_dups = pd.concat(trimmed_common_meta_dfs, axis=0)
    logger.debug("all_meta_df_with_dups.shape:  {}".format(all_meta_df_with_dups.shape))
    logger.debug("all_meta_df_with_dups.columns:  {}".format(all_meta_df_with_dups.columns))
    logger.debug("all_meta_df_with_dups.index:  {}".format(all_meta_df_with_dups.index))

    # If all metadata dfs were empty, df will be empty
    if all_meta_df_with_dups.empty:
        # Simply return unique ids
        all_meta_df = pd.DataFrame(index=all_meta_df_with_dups.index.unique())

    else:
        all_meta_df_with_dups["concat_column_for_index"] = all_meta_df_with_dups.index
        all_meta_df = all_meta_df_with_dups.copy(deep=True).drop_duplicates()
        all_meta_df.drop("concat_column_for_index", axis=1, inplace=True)
        all_meta_df_with_dups.drop("concat_column_for_index", axis=1, inplace=True)

    logger.debug("all_meta_df_with_dups.shape: {}".format(all_meta_df_with_dups.shape))
    logger.debug("all_meta_df.shape: {}".format(all_meta_df.shape))

    return (all_meta_df, all_meta_df_with_dups)


def build_mismatched_common_meta_report(common_meta_df_shapes, sources, all_meta_df, all_meta_df_with_dups):
    """
    Generate a report (dataframe) that indicates for the common metadata that does not match across the common metadata
        which source file had which of the different mismatch values

    Args:
        common_meta_df_shapes:  list of tuples that are the shapes of the common meta dataframes
        sources: list of the source files that the dataframes were loaded from
        all_meta_df: produced from build_common_all_meta_df
        all_meta_df_with_dups: produced from build_common_all_meta_df

    Returns:
        all_report_df:  dataframe indicating the mismatched row metadata values and the corresponding source file
    """
    expanded_sources = []
    for (i, shape) in enumerate(common_meta_df_shapes):
        src = sources[i]
        expanded_sources.extend([src for i in range(shape[0])])
    expanded_sources = numpy.array(expanded_sources)
    logger.debug("len(expanded_sources):  {}".format(len(expanded_sources)))

    duplicate_ids = all_meta_df.index[all_meta_df.index.duplicated(keep=False)]

    unique_duplicate_ids = duplicate_ids.unique()
    logger.debug("unique_duplicate_ids:  {}".format(unique_duplicate_ids))

    duplicate_ids_meta_df = all_meta_df.loc[unique_duplicate_ids]

    report_df_list = []
    for unique_dup_id in unique_duplicate_ids:
        rows = duplicate_ids_meta_df.loc[unique_dup_id]

        matching_row_locs = numpy.array([False for i in range(all_meta_df_with_dups.shape[0])])
        for i in range(rows.shape[0]):
            r = rows.iloc[i]
            row_comparison = r == all_meta_df_with_dups
            matching_row_locs = matching_row_locs | row_comparison.all(axis=1).values

        report_df = all_meta_df_with_dups.loc[matching_row_locs].copy()
        report_df["source_file"] = expanded_sources[matching_row_locs]
        logger.debug("report_df.shape:  {}".format(report_df.shape))
        report_df_list.append(report_df)

    all_report_df = pd.concat(report_df_list, axis=0)
    all_report_df["orig_rid"] = all_report_df.index
    all_report_df.index = pd.Index(range(all_report_df.shape[0]), name="index")
    logger.debug("all_report_df.shape:  {}".format(all_report_df.shape))
    logger.debug("all_report_df.index:  {}".format(all_report_df.index))
    logger.debug("all_report_df.columns:  {}".format(all_report_df.columns))

    return all_report_df


def assemble_concatenated_meta(concated_meta_dfs, remove_all_metadata_fields):
    """ Assemble the concatenated metadata dfs together. For example,
    if horizontally concatenating, the concatenated metadata dfs are the
    column metadata dfs. Both indices are sorted.

    Args:
        concated_meta_dfs (list of pandas dfs)

    Returns:
        all_concated_meta_df_sorted (pandas df)

    """
    # Concatenate the concated_meta_dfs
    if remove_all_metadata_fields:
        for df in concated_meta_dfs:
            df.drop(df.columns, axis=1, inplace=True)

    all_concated_meta_df = pd.concat(concated_meta_dfs, axis=0)

    # Sanity check: the number of rows in all_concated_meta_df should correspond
    # to the sum of the number of rows in the input dfs
    n_rows = all_concated_meta_df.shape[0]
    logger.debug("all_concated_meta_df.shape[0]: {}".format(n_rows))
    n_rows_cumulative = sum([df.shape[0] for df in concated_meta_dfs])
    assert n_rows == n_rows_cumulative

    # Sort the index and columns
    all_concated_meta_df_sorted = all_concated_meta_df.sort_index(axis=0).sort_index(axis=1)

    return all_concated_meta_df_sorted


def assemble_data(data_dfs, concat_direction):
    """ Assemble the data dfs together. Both indices are sorted.

    Args:
        data_dfs (list of pandas dfs)
        concat_direction (string): 'horiz' or 'vert'

    Returns:
        all_data_df_sorted (pandas df)

    """
    if concat_direction == "horiz":
        # Concatenate the data_dfs horizontally
        all_data_df = pd.concat(data_dfs, axis=1)

        # Sanity check: the number of columns in all_data_df should
        # correspond to the sum of the number of columns in the input dfs
        n_cols = all_data_df.shape[1]
        logger.debug("all_data_df.shape[1]: {}".format(n_cols))
        n_cols_cumulative = sum([df.shape[1] for df in data_dfs])
        assert n_cols == n_cols_cumulative

    elif concat_direction == "vert":

        # Concatenate the data_dfs vertically
        all_data_df = pd.concat(data_dfs, axis=0)

        # Sanity check: the number of rows in all_data_df should
        # correspond to the sum of the number of rows in the input dfs
        n_rows = all_data_df.shape[0]
        logger.debug("all_data_df.shape[0]: {}".format(n_rows))
        n_rows_cumulative = sum([df.shape[0] for df in data_dfs])
        assert n_rows == n_rows_cumulative

    # Sort both indices
    all_data_df_sorted = all_data_df.sort_index(axis=0).sort_index(axis=1)

    return all_data_df_sorted


def do_reset_ids(concatenated_meta_df, data_df, concat_direction):
    """ Reset ids in concatenated metadata and data dfs to unique integers and
    save the old ids in a metadata column.

    Note that the dataframes are modified in-place.

    Args:
        concatenated_meta_df (pandas df)
        data_df (pandas df)
        concat_direction (string): 'horiz' or 'vert'

    Returns:
        None (dfs modified in-place)

    """
    if concat_direction == "horiz":

        # Make sure cids agree between data_df and concatenated_meta_df
        assert concatenated_meta_df.index.equals(data_df.columns), (
            "cids in concatenated_meta_df do not agree with cids in data_df.")

        # Reset cids in concatenated_meta_df
        reset_ids_in_meta_df(concatenated_meta_df)

        # Replace cids in data_df with the new ones from concatenated_meta_df
        # (just an array of unique integers, zero-indexed)
        data_df.columns = pd.Index(concatenated_meta_df.index.values)

    elif concat_direction == "vert":

        # Make sure rids agree between data_df and concatenated_meta_df
        assert concatenated_meta_df.index.equals(data_df.index), (
            "rids in concatenated_meta_df do not agree with rids in data_df.")

        # Reset rids in concatenated_meta_df
        reset_ids_in_meta_df(concatenated_meta_df)

        # Replace rids in data_df with the new ones from concatenated_meta_df
        # (just an array of unique integers, zero-indexed)
        data_df.index = pd.Index(concatenated_meta_df.index.values)


def reset_ids_in_meta_df(meta_df):
    """ Meta_df is modified inplace. """

    # Record original index name, and then change it so that the column that it
    # becomes will be appropriately named
    original_index_name = meta_df.index.name
    meta_df.index.name = "old_id"

    # Reset index
    meta_df.reset_index(inplace=True)

    # Change the index name back to what it was
    meta_df.index.name = original_index_name


class MismatchCommonMetadataConcatException(Exception):
    pass

if __name__ == "__main__":
    main()

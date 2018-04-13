"""
subset_gctoo.py

Extract a subset of data from a GCToo object using string ids, integer ids,
or boolean arrays. The order of rows and columns will be preserved.
See subset.py for the command line equivalent.

"""
import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.GCToo as GCToo

__author__ = "Lev Litichevskiy"
__email__ = "lev@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)


def subset_gctoo(gctoo, row_bool=None, col_bool=None, rid=None, cid=None,
                ridx=None, cidx=None, exclude_rid=None, exclude_cid=None):
    """ Extract a subset of data from a GCToo object in a variety of ways.
    The order of rows and columns will be preserved.

    Args:
        gctoo (GCToo object)
        row_bool (list of bools): length must equal gctoo.data_df.shape[0]
        col_bool (list of bools): length must equal gctoo.data_df.shape[1]
        rid (list of strings): rids to include
        cid (list of strings): cids to include
        ridx (list of integers): row integer ids to include
        cidx (list of integers): col integer ids to include
        exclude_rid (list of strings): rids to exclude
        exclude_cid (list of strings): cids to exclude

    Returns:
        out_gctoo (GCToo object): gctoo after subsetting
    """
    assert sum([(rid is not None), (row_bool is not None), (ridx is not None)]) <= 1, (
        "Only one of rid, row_bool, and ridx can be provided.")
    assert sum([(cid is not None), (col_bool is not None), (cidx is not None)]) <= 1, (
        "Only one of cid, col_bool, and cidx can be provided.")

    # Figure out what rows and columns to keep
    rows_to_keep = get_rows_to_keep(gctoo, rid, row_bool, ridx, exclude_rid)
    cols_to_keep = get_cols_to_keep(gctoo, cid, col_bool, cidx, exclude_cid)

    # Convert labels to boolean array to preserve order
    rows_to_keep_bools = gctoo.data_df.index.isin(rows_to_keep)
    cols_to_keep_bools = gctoo.data_df.columns.isin(cols_to_keep)

    # Make the output gct
    out_gctoo = GCToo.GCToo(
        src=gctoo.src, version=gctoo.version,
        data_df=gctoo.data_df.loc[rows_to_keep_bools, cols_to_keep_bools],
        row_metadata_df=gctoo.row_metadata_df.loc[rows_to_keep_bools, :],
        col_metadata_df=gctoo.col_metadata_df.loc[cols_to_keep_bools, :])

    assert out_gctoo.data_df.size > 0, "Subsetting yielded an empty gct!"

    logger.info(("Initial GCToo with {} rows and {} columns subsetted down to " +
                 "{} rows and {} columns.").format(
                      gctoo.data_df.shape[0], gctoo.data_df.shape[1],
                      out_gctoo.data_df.shape[0], out_gctoo.data_df.shape[1]))

    return out_gctoo


def get_rows_to_keep(gctoo, rid=None, row_bool=None, ridx=None, exclude_rid=None):
    """ Figure out based on the possible row inputs which rows to keep.

    Args:
        gctoo (GCToo object):
        rid (list of strings):
        row_bool (boolean array):
        ridx (list of integers):
        exclude_rid (list of strings):

    Returns:
        rows_to_keep (list of strings): row ids to be kept

    """
    # Use rid if provided
    if rid is not None:
        assert type(rid) == list, "rid must be a list. rid: {}".format(rid)

        rows_to_keep = [gctoo_row for gctoo_row in gctoo.data_df.index if gctoo_row in rid]

        # Tell user if some rids not found
        num_missing_rids = len(rid) - len(rows_to_keep)
        if num_missing_rids != 0:
            logger.info("{} rids were not found in the GCT.".format(num_missing_rids))

    # Use row_bool if provided
    elif row_bool is not None:

        assert len(row_bool) == gctoo.data_df.shape[0], (
            "row_bool must have length equal to gctoo.data_df.shape[0]. " +
            "len(row_bool): {}, gctoo.data_df.shape[0]: {}".format(
                len(row_bool), gctoo.data_df.shape[0]))
        rows_to_keep = gctoo.data_df.index[row_bool].values

    # Use ridx if provided
    elif ridx is not None:

        assert type(ridx[0]) is int, (
            "ridx must be a list of integers. ridx[0]: {}, " +
            "type(ridx[0]): {}").format(ridx[0], type(ridx[0]))

        assert max(ridx) <= gctoo.data_df.shape[0], (
            "ridx contains an integer larger than the number of rows in " +
            "the GCToo. max(ridx): {}, gctoo.data_df.shape[0]: {}").format(
                max(ridx), gctoo.data_df.shape[0])

        rows_to_keep = gctoo.data_df.index[ridx].values

    # If rid, row_bool, and ridx are all None, return all rows
    else:
        rows_to_keep = gctoo.data_df.index.values

    # Use exclude_rid if provided
    if exclude_rid is not None:

        # Keep only those rows that are not in exclude_rid
        rows_to_keep = [row_to_keep for row_to_keep in rows_to_keep if row_to_keep not in exclude_rid]

    return rows_to_keep


def get_cols_to_keep(gctoo, cid=None, col_bool=None, cidx=None, exclude_cid=None):
    """ Figure out based on the possible columns inputs which columns to keep.

    Args:
        gctoo (GCToo object):
        cid (list of strings):
        col_bool (boolean array):
        cidx (list of integers):
        exclude_cid (list of strings):

    Returns:
        cols_to_keep (list of strings): col ids to be kept

    """

    # Use cid if provided
    if cid is not None:
        assert type(cid) == list, "cid must be a list. cid: {}".format(cid)

        cols_to_keep = [gctoo_col for gctoo_col in gctoo.data_df.columns if gctoo_col in cid]

        # Tell user if some cids not found
        num_missing_cids = len(cid) - len(cols_to_keep)
        if num_missing_cids != 0:
            logger.info("{} cids were not found in the GCT.".format(num_missing_cids))

    # Use col_bool if provided
    elif col_bool is not None:

        assert len(col_bool) == gctoo.data_df.shape[1], (
            "col_bool must have length equal to gctoo.data_df.shape[1]. " +
            "len(col_bool): {}, gctoo.data_df.shape[1]: {}".format(
                len(col_bool), gctoo.data_df.shape[1]))
        cols_to_keep = gctoo.data_df.columns[col_bool].values

    # Use cidx if provided
    elif cidx is not None:

        assert type(cidx[0]) is int, (
            "cidx must be a list of integers. cidx[0]: {}, " +
            "type(cidx[0]): {}").format(cidx[0], type(cidx[0]))

        assert max(cidx) <= gctoo.data_df.shape[1], (
            "cidx contains an integer larger than the number of columns in " +
            "the GCToo. max(cidx): {}, gctoo.data_df.shape[1]: {}").format(
                max(cidx), gctoo.data_df.shape[1])

        cols_to_keep = gctoo.data_df.columns[cidx].values

    # If cid, col_bool, and cidx are all None, return all columns
    else:
        cols_to_keep = gctoo.data_df.columns.values

    # Use exclude_cid if provided
    if exclude_cid is not None:

        # Keep only those columns that are not in exclude_cid
        cols_to_keep = [col_to_keep for col_to_keep in cols_to_keep if col_to_keep not in exclude_cid]

    return cols_to_keep

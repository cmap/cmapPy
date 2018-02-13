"""
slice_gctoo.py

Extract a subset of data from a GCToo object using ids or boolean arrays.
See slice_gct.py for the command line equivalent.

"""
import logging
import pandas as pd
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.GCToo as GCToo

__author__ = "Lev Litichevskiy"
__email__ = "lev@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)


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
        src=gctoo.src, version=gctoo.version,
        data_df=gctoo.data_df.loc[rows_to_keep_bools, cols_to_keep_bools],
        row_metadata_df=gctoo.row_metadata_df.loc[rows_to_keep_bools, :],
        col_metadata_df=gctoo.col_metadata_df.loc[cols_to_keep_bools, :])

    logger.info(("Initial GCToo with {} rows and {} columns sliced down to " +
                 "{} rows and {} columns.").format(
                      gctoo.data_df.shape[0], gctoo.data_df.shape[1],
                      out_gctoo.data_df.shape[0], out_gctoo.data_df.shape[1]))

    return out_gctoo
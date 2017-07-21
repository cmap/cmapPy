import logging
import setup_GCToo_logger as setup_logger
import pandas as pd
import numpy as np
import os

__author__ = "Lev Litichevskiy"
__email__ = "lev@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)

# Only writes GCT1.3
VERSION = "1.3"

def write_gct(gctoo, out_fname, data_null="NaN", metadata_null="-666", 
    filler_null="-666", data_float_format=":.4f"):
    """
    Essentially the same as write() method; enables user to call write_gct() from
    cmapPy instead of write_gct.write()

    Included as a separate method for backwards compatibility.
    """
    write(gctoo, out_fname, data_null="NaN", metadata_null="-666", 
    filler_null="-666", data_float_format=":.4f")

def write(gctoo, out_fname, data_null="NaN", metadata_null="-666", filler_null="-666", data_float_format=":.4f"):
    """Write a gctoo object to a gct file.

    Args:
        gctoo (gctoo object)
        out_fname (string): filename for output gct file
        data_null (string): how to represent missing values in the data (default = "NaN")
        metadata_null (string): how to represent missing values in the metadata (default = "-666")
        filler_null (string): what value to fill the top-left filler block with (default = "-666")
        data_float_format (string): how many decimal points to keep in representing data
            (default = 4 digits; None will keep all digits)

    Returns:
        None

    """
    # Create handle for output file
    if not out_fname.endswith(".gct"):
        out_fname += ".gct"
    f = open(out_fname, "wb")

    # Write first two lines
    dims = [str(gctoo.data_df.shape[0]), str(gctoo.data_df.shape[1]),
            str(gctoo.row_metadata_df.shape[1]), str(gctoo.col_metadata_df.shape[1])]
    write_version_and_dims(VERSION, dims, f)

    # Write top half of the gct
    write_top_half(f, gctoo.row_metadata_df, gctoo.col_metadata_df,
                   metadata_null, filler_null)

    # Write bottom half of the gct
    write_bottom_half(f, gctoo.row_metadata_df, gctoo.data_df,
                      data_null, data_float_format, metadata_null)

    f.close()
    logger.info("GCT has been written to {}".format(out_fname))


def write_version_and_dims(version, dims, f):
    """Write first two lines of gct file.

    Args:
        version (string): 1.3 by default
        dims (list of strings): length = 4
        f (file handle): handle of output file
    Returns:
        nothing
    """
    f.write(("#" + version + "\n"))
    f.write((dims[0] + "\t" + dims[1] + "\t" + dims[2] + "\t" + dims[3] + "\n"))


def write_top_half(f, row_metadata_df, col_metadata_df, metadata_null, filler_null):
    """ Write the top half of the gct file: top-left filler values, row metadata
    headers, and top-right column metadata.

    Args:
        f (file handle): handle for output file
        row_metadata_df (pandas df)
        col_metadata_df (pandas df)
        metadata_null (string): how to represent missing values in the metadata
        filler_null (string): what value to fill the top-left filler block with

    Returns:
        None
    """
    # Initialize the top half of the gct including the third line
    size_of_top_half_df = (1 + col_metadata_df.shape[1],
                           1 + row_metadata_df.shape[1] + col_metadata_df.shape[0])
    top_half_df = pd.DataFrame(np.full(size_of_top_half_df, filler_null, dtype=object))

    # Assemble the third line of the gct: "id", then rhds, then cids
    top_half_df.iloc[0, :] = np.hstack(("id", row_metadata_df.columns.values, col_metadata_df.index.values))

    # Insert the chds
    top_half_df.iloc[range(1, top_half_df.shape[0]), 0] = col_metadata_df.columns.values

    # Insert the column metadata, but first convert to strings and replace NaNs
    col_metadata_indices = (range(1, top_half_df.shape[0]),
                            range(1 + row_metadata_df.shape[1], top_half_df.shape[1]))
    top_half_df.iloc[col_metadata_indices[0], col_metadata_indices[1]] = (
        col_metadata_df.astype(str).replace("nan", value=metadata_null).T.values)

    # Write top_half_df to file
    top_half_df.to_csv(f, header=False, index=False, sep="\t")


def write_bottom_half(f, row_metadata_df, data_df, data_null, data_float_format, metadata_null):
    """ Write the bottom half of the gct file: row metadata and data.

    Args:
        f (file handle): handle for output file
        row_metadata_df (pandas df)
        data_df (pandas df)
        data_null (string): how to represent missing values in the data
        metadata_null (string): how to represent missing values in the metadata
        data_float_format (string): how many decimal points to keep in representing data

    Returns:
        None
    """
    # Initialize the bottom half of the gct
    size_of_bottom_half_df = (row_metadata_df.shape[0],
                              1 + row_metadata_df.shape[1] + data_df.shape[1])
    bottom_half_df = pd.DataFrame(np.full(size_of_bottom_half_df, metadata_null, dtype=object))

    # Insert the rids
    bottom_half_df.iloc[:, 0] = row_metadata_df.index.values

    # Insert the row metadata, but first convert to strings and replace NaNs
    row_metadata_col_indices = range(1, 1 + row_metadata_df.shape[1])
    bottom_half_df.iloc[:, row_metadata_col_indices] = (
        row_metadata_df.astype(str).replace("nan", value=metadata_null).values)

    # Insert the data
    data_col_indices = range(1 + row_metadata_df.shape[1], bottom_half_df.shape[1])
    bottom_half_df.iloc[:, data_col_indices] = data_df.values

    # Write bottom_half_df to file
    bottom_half_df.to_csv(f, header=False, index=False, sep="\t",
                          na_rep=data_null,
                          float_format=data_float_format)


def append_dims_and_file_extension(fname, data_df):
    """Append dimensions and file extension to output filename.
    N.B. Dimensions are cols x rows.

    Args:
        fname (string): output filename
        data_df (pandas df)
    Returns:
        out_fname (string): output filename with matrix dims and .gct appended
    """
    # If there's no .gct at the end of output file name, add the dims and .gct
    if not fname.endswith(".gct"):
        out_fname = '{0}_n{1}x{2}.gct'.format(fname, data_df.shape[1], data_df.shape[0])
        return out_fname

    # Otherwise, only add the dims
    else:
        basename = os.path.splitext(fname)[0]
        out_fname = '{0}_n{1}x{2}.gct'.format(basename, data_df.shape[1], data_df.shape[0])
        return out_fname

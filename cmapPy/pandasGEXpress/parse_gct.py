""" Reads in a gct file as a gctoo object.

The main method is parse. parse_into_3_dfs creates the row
metadata, column metadata, and data dataframes, while the
assemble_multi_index_df method in GCToo.py assembles them.

1) Example GCT v1.3:
        ----- start of file ------
        #1.3
        96 36 9 15
        ---------------------------------------------------
        |id|        rhd          |          cid           |
        ---------------------------------------------------
        |  |                     |                        |
        |c |                     |                        |
        |h |      (blank)        |      col_metadata      |
        |d |                     |                        |
        |  |                     |                        |
        ---------------------------------------------------
        |  |                     |                        |
        |r |                     |                        |
        |i |    row_metadata     |          data          |
        |d |                     |                        |
        |  |                     |                        |
        ---------------------------------------------------
        ----- end of file ------

        Notes:
        - line 1 of file ("#1.3") refers to the version number 
        - line 2 of file ("96 36 9 15") refers to the following:
                -96 = number of data rows       
                -36 = number of data columns       
                -9 = number of row metadata fields (+1 for the 'id' column -- first column)        
                -15 = number of col metadata fields (+1 for the 'id' row -- first row)
        - Once read into a DataFrame, col_metadata_df is stored as the transpose of how it looks in the gct file.
                That is, col_metadata_df.shape = (num_cid, num_chd).

2) Example GCT v1.2

        ----- start of file ------
        #1.2
        96 36 
        -----------------------------------------------
        |"NAME" |"Description"|          cid           |
        -----------------------------------------------
        |   r   |             |                        |
        |   i   |             |                        |
        |   d   |row_metadata |         data           |
        |       |             |                        |
        |       |             |                        |
        -----------------------------------------------

        ----- end of file ------
        Notes:
        - line 1 of file ("#1.3") refers to the version number 
        - line 2 of file ("96 36 9 15") refers to the following:
                -96 = number of data rows   
                -36 = number of data columns   

"""

import logging
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger
import pandas as pd
import numpy as np 
import os.path
import GCToo 

__author__ = "Lev Litichevskiy, Oana Enache"
__email__ = "lev@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)

# What to label the index and columns of the component dfs
row_index_name = "rid"
column_index_name = "cid"
row_header_name = "rhd"
column_header_name = "chd"
DATA_TYPE = np.float32


def parse(file_path, convert_neg_666=True, rid=None, cid=None, make_multiindex=False):
    """ The main method.

    Args:
        - file_path (string): full path to gct(x) file you want to parse
        - convert_neg_666 (bool): whether to convert -666 values to numpy.nan
            (see Note below for more details). Default = True.
        - rid (list of strings): list of row ids to specifically keep  None keeps all rids
        - cid (list of strings): list of col ids to specifically keep, None keeps all cids
        - make_multiindex (bool): whether to create a multi-index df combining
            the 3 component dfs

    Returns:
        gctoo_obj (GCToo object)

    Note: why is convert_neg_666 even a thing?
        In CMap--for somewhat obscure historical reasons--we use "-666" as our null value
        for metadata. However (so that users can take full advantage of pandas' methods,
        including those for filtering nan's etc) we provide the option of converting these
        into numpy.nan values, the pandas default.

    """
    # Throw error if user attempts to slice
    if (rid is not None) or (cid is not None):
        error_msg = ("Slicing is not available through parse for .gct files; if you'd like to slice, " +
            "please parse the entire file in (you have to do this anyway!) and then use methods from " + 
            "the slice_gct module.")
        logger.error(error_msg)
        raise(Exception(error_msg))


    nan_values = [
        "#N/A", "N/A", "NA", "#NA", "NULL", "NaN", "-NaN",
        "nan", "-nan", "#N/A!", "na", "NA", "None"]

    # Add "-666" to the list of NaN values
    if convert_neg_666:
        nan_values.append("-666")

    # Verify that the gct path exists
    if not os.path.exists(file_path):
        err_msg = "The given path to the gct file cannot be found. gct_path: {}"
        logger.error(err_msg.format(file_path))
        raise(Exception(err_msg.format(file_path)))
    logger.info("Reading GCT: {}".format(file_path))

    # Read version and dimensions
    (version, num_data_rows, num_data_cols,
     num_row_metadata, num_col_metadata) = read_version_and_dims(file_path)

    # Read in metadata and data
    (row_metadata, col_metadata, data) = parse_into_3_df(
        file_path, num_data_rows, num_data_cols,
        num_row_metadata, num_col_metadata, nan_values)

    # Create the gctoo object and assemble 3 component dataframes
    gctoo_obj = create_gctoo_obj(file_path, version,
        row_metadata, col_metadata, data, make_multiindex)

    return gctoo_obj


def read_version_and_dims(file_path):
    # Open file
    f = open(file_path, "rb")

    # Get version from the first line
    version = f.readline().strip().lstrip("#")

    if version not in ["1.3", "1.2"]:
        err_msg = ("Only GCT1.2 and 1.3 are supported. The first row of the GCT " +
                   "file must simply be (without quotes) '#1.3' or '#1.2'")
        logger.error(err_msg.format(version))
        raise(Exception(err_msg.format(version)))

    # Convert version to a string
    version_as_string = "GCT" + str(version)

    # Read dimensions from the second line
    dims = f.readline().strip().split("\t")

    # Close file
    f.close()

    # Check that the second row is what we expect
    if version == "1.2" and len(dims) != 2:
        error_msg = "GCT1.2 should have 2 dimension-related entries in row 2. dims: {}"
        logger.error(error_msg.format(dims))
        raise(Exception(error_msg.format(dims)))
    elif version == "1.3" and len(dims) != 4: 
        error_msg = "GCT1.3 should have 4 dimension-related entries in row 2. dims: {}"
        logger.error(error_msg.format(dims))
        raise(Exception(error_msg.format(dims)))

    # Explicitly define each dimension
    num_data_rows = int(dims[0])
    num_data_cols = int(dims[1])
    if len(dims) == 4:
        num_row_metadata = int(dims[2])
        num_col_metadata = int(dims[3])
    else: 
        num_row_metadata = 1
        num_col_metadata = 0 

    # Return version and dimensions
    return version_as_string, num_data_rows, num_data_cols, num_row_metadata, num_col_metadata


def parse_into_3_df(file_path, num_data_rows, num_data_cols, num_row_metadata, num_col_metadata, nan_values):
    # Read the gct file beginning with line 3
    full_df = pd.read_csv(file_path, sep="\t", header=None, skiprows=2,
                          dtype=str, na_values=nan_values, keep_default_na=False)

    # Check that full_df is the size we expect
    assert full_df.shape == (num_col_metadata + num_data_rows + 1,
                             num_row_metadata + num_data_cols + 1), (
        ("The shape of full_df is not as expected: data is {} x {} " +
         "but there are {} row meta fields and {} col fields").format(
            num_data_rows, num_data_cols, num_row_metadata, num_col_metadata))

    # Assemble metadata dataframes
    row_metadata = assemble_row_metadata(full_df, num_col_metadata, num_data_rows, num_row_metadata)
    col_metadata = assemble_col_metadata(full_df, num_col_metadata, num_row_metadata, num_data_cols)

    # Assemble data dataframe
    data = assemble_data(full_df, num_col_metadata, num_data_rows, num_row_metadata, num_data_cols)

    # Return 3 dataframes
    return row_metadata, col_metadata, data


def assemble_row_metadata(full_df, num_col_metadata, num_data_rows, num_row_metadata):
    # Extract values
    row_metadata_row_inds = range(num_col_metadata + 1, num_col_metadata + num_data_rows + 1)
    row_metadata_col_inds = range(1, num_row_metadata + 1)
    row_metadata = full_df.iloc[row_metadata_row_inds, row_metadata_col_inds]

    # Create index from the first column of full_df (after the filler block)
    row_metadata.index = full_df.iloc[row_metadata_row_inds, 0]

    # Create columns from the top row of full_df (before cids start)
    row_metadata.columns = full_df.iloc[0, row_metadata_col_inds]

    # Rename the index name and columns name
    row_metadata.index.name = row_index_name
    row_metadata.columns.name = row_header_name

    # Convert metadata to numeric if possible
    row_metadata = row_metadata.apply(lambda x: pd.to_numeric(x, errors="ignore"))

    return row_metadata


def assemble_col_metadata(full_df, num_col_metadata, num_row_metadata, num_data_cols):

    # Extract values
    col_metadata_row_inds = range(1, num_col_metadata + 1)
    col_metadata_col_inds = range(num_row_metadata + 1, num_row_metadata + num_data_cols + 1)
    col_metadata = full_df.iloc[col_metadata_row_inds, col_metadata_col_inds]

    # Transpose so that samples are the rows and headers are the columns
    col_metadata = col_metadata.T

    # Create index from the top row of full_df (after the filler block)
    col_metadata.index = full_df.iloc[0, col_metadata_col_inds]

    # Create columns from the first column of full_df (before rids start)
    col_metadata.columns = full_df.iloc[col_metadata_row_inds, 0]

    # Rename the index name and columns name
    col_metadata.index.name = column_index_name
    col_metadata.columns.name = column_header_name

    # Convert metadata to numeric if possible
    col_metadata = col_metadata.apply(lambda x: pd.to_numeric(x, errors="ignore"))

    return col_metadata


def assemble_data(full_df, num_col_metadata, num_data_rows, num_row_metadata, num_data_cols):
    # Extract values
    data_row_inds = range(num_col_metadata + 1, num_col_metadata + num_data_rows + 1)
    data_col_inds = range(num_row_metadata + 1, num_row_metadata + num_data_cols + 1)
    data = full_df.iloc[data_row_inds, data_col_inds]

    # Create index from the first column of full_df (after the filler block)
    data.index = full_df.iloc[data_row_inds, 0]

    # Create columns from the top row of full_df (after the filler block)
    data.columns = full_df.iloc[0, data_col_inds]

    # Convert from str to float
    try:
        data = data.astype(DATA_TYPE)
    except:
        # If that fails, return the first value that could not be converted
        for col in data:
            try:
                data[col].astype(DATA_TYPE)
            except:
                for row_idx, val in enumerate(data[col]):
                    try:
                        DATA_TYPE(val)
                    except:
                        bad_row_label = data[col].index[row_idx]
                        err_msg = ("First instance of value that could not be converted: " +
                                   "data.loc['{}', '{}'] = '{}'\nAdd to nan_values if you wish " +
                                   "for this value to be considered NaN.").format(bad_row_label, col, val)
                        logger.error(err_msg)
                        raise(Exception(err_msg))

    # Rename the index name and columns name
    data.index.name = row_index_name
    data.columns.name = column_index_name

    return data


def create_gctoo_obj(file_path, version, row_metadata_df, col_metadata_df, data_df, make_multiindex):

    # Move dataframes into GCToo object
    gctoo_obj = GCToo.GCToo(src=file_path,
                            version=version,
                            row_metadata_df=row_metadata_df,
                            col_metadata_df=col_metadata_df,
                            data_df=data_df, make_multiindex=make_multiindex)
    return gctoo_obj


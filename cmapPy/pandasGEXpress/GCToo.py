"""
DATA:
-----------------------------
|  |          cid           |
-----------------------------
|  |                        |
|r |                        |
|i |          data          |
|d |                        |
|  |                        |
-----------------------------
ROW METADATA:
--------------------------
|id|        rhd          |
--------------------------
|  |                     |
|r |                     |
|i |    row_metadata     |
|d |                     |
|  |                     |
--------------------------
COLUMN METADATA:
N.B. The df is transposed from how it looks in a gct file.
---------------------
|id|      chd       |
---------------------
|  |                |
|  |                |
|  |                |
|c |                |
|i |  col_metadata  |
|d |                |
|  |                |
|  |                |
|  |                |
---------------------

N.B. rids, cids, rhds, and chds must be:
- unique
- matching in both content & order everywhere they're found 
"""
import numpy as np
import pandas as pd
import logging
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger

__authors__ = 'Oana Enache, Lev Litichevskiy, Dave Lahr'
__email__ = 'dlahr@broadinstitute.org'

class GCToo(object):
    """Class representing parsed gct(x) objects as pandas dataframes.
    Contains 3 component dataframes (row_metadata_df, column_metadata_df,
    and data_df) as well as an assembly of these 3 into a multi index df
    that provides an alternate way of selecting data.
    """
    def __init__(self, data_df, row_metadata_df, col_metadata_df,
                 src=None, version=None, make_multiindex=False, logger_name=setup_logger.LOGGER_NAME):

        self.logger = logging.getLogger(logger_name)

        self.src = src
        self.version = version
        self.row_metadata_df = row_metadata_df
        self.col_metadata_df = col_metadata_df
        self.data_df = data_df
        self.multi_index_df = None

        for df_field in ["row_metadata_df", "col_metadata_df", "data_df"]:
            df = self.__dict__[df_field]
            self.check_df(df)

        # check rids match in data & meta
        self.id_match_check(self.data_df, self.row_metadata_df, "row")

        # check cids match in data & meta
        self.id_match_check(self.data_df, self.col_metadata_df, "col")

        if make_multiindex:
            self.assemble_multi_index_df()

        self._initialized = True

    def __setattr__(self, name, value):
        if "_initialized" in self.__dict__ and self._initialized:
            if name in ["data_df", "row_metadata_df", "col_metadata_df"]:
                if self.check_df(value):
                    if (name == "row_metadata_df" and self.id_match_check(self.data_df, value, "row")):
                        value = value.reindex(self.data_df.index)
                        super(GCToo, self).__setattr__(name, value)
                    elif (name == "col_metadata_df" and self.id_match_check(self.data_df, value, "col")):
                        value = value.reindex(self.data_df.columns)
                        super(GCToo, self).__setattr__(name, value)
                    elif (name == "data_df" and (self.id_match_check(value, self.row_metadata_df, "row")
                                                and self.id_match_check(value, self.col_metadata_df, "col"))):
                        # in this case we need to reindex both row/col metadata so that indexes are ordered
                        # the same as the new data_df
                        super(GCToo, self).__setattr__("row_metadata_df", self.row_metadata_df.reindex(value.index))
                        super(GCToo, self).__setattr__("col_metadata_df", self.col_metadata_df.reindex(value.index))
            elif name == "multi_index_df":
                msg = ("Cannot reassign value of multi_index_df attribute; "  +
                    "if you'd like a new multiindex df, please create a new GCToo instance" +
                    "with appropriate data_df, row_metadata_df, and col_metadata_df fields.")
                self.logger.error(msg)
                raise Exception("GCToo.__setattr__: " + msg)
            else:
                super(GCToo, self).__setattr__(name, value)
        else: # for init we first want to set everything
            super(GCToo, self).__setattr__(name, value)

    def check_df(self, df):
        """
        Verifies that df is a pandas DataFrame instance and
        that its index and column values are unique.
        """
        if isinstance(df, pd.DataFrame):
            if not df.index.is_unique:
                repeats = df.index[df.index.duplicated()].values
                msg = "Index values must be unique but aren't. The following entries appear more than once: {}".format(repeats)
                self.logger.error(msg)
                raise Exception("GCToo GCToo.check_df " + msg)
            if not df.columns.is_unique:
                repeats = df.columns[df.columns.duplicated()].values
                msg = "Columns values must be unique but aren't. The following entries appear more than once: {}".format(repeats)
                raise Exception("GCToo GCToo.check_df " + msg)
            else:
                return True
        else:
            msg = "expected Pandas DataFrame, got something else:  {}  of type:  {}".format(df, type(df))
            self.logger.error(msg)
            raise Exception("GCToo GCToo.check_df " + msg)

    def id_match_check(self, data_df, meta_df, dim):
        """
        Verifies that id values match between:
            - row case: index of data_df & index of row metadata
            - col case: columns of data_df & index of column metadata
        """
        if dim == "row":
            if len(data_df.index) == len(meta_df.index) and set(data_df.index) == set(meta_df.index):
                return True
            else:
                msg = ("The rids are inconsistent between data_df and row_metadata_df.\n" +
                 "data_df.index.values:\n{}\nrow_metadata_df.index.values:\n{}").format(data_df.index.values, meta_df.index.values)
                self.logger.error(msg)
                raise Exception("GCToo GCToo.id_match_check " + msg)
        elif dim == "col":
            if len(data_df.columns) == len(meta_df.index) and set(data_df.columns) == set(meta_df.index):
                return True
            else:
                msg = ("The cids are inconsistent between data_df and col_metadata_df.\n" +
                 "data_df.columns.values:\n{}\ncol_metadata_df.index.values:\n{}").format(data_df.columns.values, meta_df.index.values)
                self.logger.error(msg)
                raise Exception("GCToo GCToo.id_match_check " + msg)

    def __str__(self):
        """Prints a string representation of a GCToo object."""
        version = "{}\n".format(self.version)
        source = "src: {}\n".format(self.src)


        data = "data_df: [{} rows x {} columns]\n".format(
        self.data_df.shape[0], self.data_df.shape[1])

        row_meta = "row_metadata_df: [{} rows x {} columns]\n".format(
        self.row_metadata_df.shape[0], self.row_metadata_df.shape[1])

        col_meta = "col_metadata_df: [{} rows x {} columns]".format(
        self.col_metadata_df.shape[0], self.col_metadata_df.shape[1])

        full_string = (version + source + data + row_meta + col_meta)
        return full_string

    def assemble_multi_index_df(self):
        """Assembles three component dataframes into a multiindex dataframe.
        Sets the result to self.multi_index_df.
        IMPORTANT: Cross-section ("xs") is the best command for selecting
        data. Be sure to use the flag "drop_level=False" with this command,
        or else the dataframe that is returned will not have the same
        metadata as the input.
        N.B. "level" means metadata header.
        N.B. "axis=1" indicates column annotations.
        Examples:
            1) Select the probe with pr_lua_id="LUA-3404":
            lua3404_df = multi_index_df.xs("LUA-3404", level="pr_lua_id", drop_level=False)
            2) Select all DMSO samples:
            DMSO_df = multi_index_df.xs("DMSO", level="pert_iname", axis=1, drop_level=False)
        """
        #prepare row index
        self.logger.debug("Row metadata shape: {}".format(self.row_metadata_df.shape))
        self.logger.debug("Is empty? {}".format(self.row_metadata_df.empty))
        row_copy = pd.DataFrame(self.row_metadata_df.index) if self.row_metadata_df.empty else self.row_metadata_df.copy()
        row_copy["rid"] = row_copy.index
        row_index = pd.MultiIndex.from_arrays(row_copy.T.values, names=row_copy.columns)

        #prepare column index
        self.logger.debug("Col metadata shape: {}".format(self.col_metadata_df.shape))
        col_copy = pd.DataFrame(self.col_metadata_df.index) if self.col_metadata_df.empty else self.col_metadata_df.copy()
        col_copy["cid"] = col_copy.index
        transposed_col_metadata = col_copy.T
        col_index = pd.MultiIndex.from_arrays(transposed_col_metadata.values, names=transposed_col_metadata.index)

        # Create multi index dataframe using the values of data_df and the indexes created above
        self.logger.debug("Data df shape: {}".format(self.data_df.shape))
        self.multi_index_df = pd.DataFrame(data=self.data_df.values, index=row_index, columns=col_index)


def multi_index_df_to_component_dfs(multi_index_df, rid="rid", cid="cid"):
    """ Convert a multi-index df into 3 component dfs. """

    # Id level of the multiindex will become the index
    rids = list(multi_index_df.index.get_level_values(rid))
    cids = list(multi_index_df.columns.get_level_values(cid))

    # It's possible that the index and/or columns of multi_index_df are not
    # actually multi-index; need to check for this
    if isinstance(multi_index_df.index, pd.core.index.MultiIndex):

        # If so, drop rid because it won't go into the body of the metadata
        mi_df_index = multi_index_df.index.droplevel(rid)

        # Names of the multiindex levels become the headers
        rhds = list(mi_df_index.names)

        # Assemble metadata values
        row_metadata = np.array([mi_df_index.get_level_values(level).values for level in list(rhds)]).T

    # If the index is not multi-index, then rhds and row metadata should be empty
    else:
        rhds = []
        row_metadata = []

    # Check if columns of multi_index_df are in fact multi-index
    if isinstance(multi_index_df.columns, pd.core.index.MultiIndex):

        # If so, drop cid because it won't go into the body of the metadata
        mi_df_columns = multi_index_df.columns.droplevel(cid)

        # Names of the multiindex levels become the headers
        chds = list(mi_df_columns.names)

        # Assemble metadata values
        col_metadata = np.array([mi_df_columns.get_level_values(level).values for level in list(chds)]).T

    # If the columns are not multi-index, then rhds and row metadata should be empty
    else:
        chds = []
        col_metadata = []

    # Create component dfs
    row_metadata_df = pd.DataFrame.from_records(row_metadata, index=pd.Index(rids, name="rid"), columns=pd.Index(rhds, name="rhd"))
    col_metadata_df = pd.DataFrame.from_records(col_metadata, index=pd.Index(cids, name="cid"), columns=pd.Index(chds, name="chd"))
    data_df = pd.DataFrame(multi_index_df.values, index=pd.Index(rids, name="rid"), columns=pd.Index(cids, name="cid"))

    return data_df, row_metadata_df, col_metadata_df
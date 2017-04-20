"""
Slices a random subset of a GCToo instance of a user-specified size. 
"""
import logging
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger
import numpy
import GCToo 


__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)

def make_specified_size_gctoo(og_gctoo, num_entries, dim):
	"""
	Subsets a GCToo instance along either rows or columns to obtain a specified size.

	Input:
		- og_gctoo (GCToo): a GCToo instance 
		- num_entries (int): the number of entries to keep
		- dim (str): the dimension along which to subset. Must be "row" or "col"

	Output:
		- new_gctoo (GCToo): the GCToo instance subsetted as specified. 
	"""	
	assert dim in ["row", "col"], "dim specified must be either 'row' or 'col'"

	dim_index = 0 if "row" == dim else 1
	assert num_entries <= og_gctoo.data_df.shape[dim_index], ("number of entries must be smaller than dimension being "
		"subsetted - num_entries:  {}  dim:  {}  dim_index:  {}  og_gctoo.data_df.shape[dim_index]:  {}".format(
		num_entries, dim, dim_index, og_gctoo.data_df.shape[dim_index]))

	if dim == "col":
		columns = [x for x in og_gctoo.data_df.columns.values]
		numpy.random.shuffle(columns)
		columns = columns[0:num_entries]
		rows = og_gctoo.data_df.index.values
	else:
		rows = [x for x in og_gctoo.data_df.index.values]
		numpy.random.shuffle(rows)
		rows = rows[0:num_entries]
		columns = og_gctoo.data_df.columns.values

	new_data_df = og_gctoo.data_df.loc[rows, columns]
	new_row_meta = og_gctoo.row_metadata_df.loc[rows]
	new_col_meta = og_gctoo.col_metadata_df.loc[columns]
	
	logger.debug("after slice - new_col_meta.shape: {}  new_row_meta.shape:  {}".format(new_col_meta.shape, new_row_meta.shape))

	# make & return new gctoo instance
	new_gctoo = GCToo.GCToo(data_df=new_data_df, row_metadata_df=new_row_meta, col_metadata_df=new_col_meta)

	return new_gctoo

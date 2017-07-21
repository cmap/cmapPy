import logging 
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger 
import h5py
import numpy
import GCToo 

__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)

src_attr = "src"
data_matrix_node = "/0/DATA/0/matrix"
row_meta_group_node = "/0/META/ROW"
col_meta_group_node = "/0/META/COL"
version_attr = "version"
version_number = "GCTX1.0"

def write_gctx(gctoo_object, out_file_name, convert_back_to_neg_666 = True):
	"""
	Essentially the same as write() method; enables user to call write_gctx() from
	cmapPy instead of write_gctx.write()

	Included as a separate method for backwards compatibility.
	"""
	write(gctoo_object, out_file_name, convert_back_to_neg_666)

def write(gctoo_object, out_file_name, convert_back_to_neg_666 = True):
	"""
	Writes a GCToo instance to specified file.

	Input:
		- gctoo_object (GCToo): A GCToo instance.
		- out_file_name (str): file name to write gctoo_object to.
	"""
	# make sure out file has a .gctx suffix
	gctx_out_name = add_gctx_to_out_name(out_file_name)
	
	# open an hdf5 file to write to 
	hdf5_out = h5py.File(gctx_out_name, "w")

	# write version
	write_version(hdf5_out)

	# write src 
	write_src(hdf5_out, gctoo_object, gctx_out_name)

	# write data matrix
	hdf5_out.create_dataset(data_matrix_node, data=gctoo_object.data_df.transpose().as_matrix())

	# write col metadata
	write_metadata(hdf5_out, "col", gctoo_object.col_metadata_df, convert_back_to_neg_666)

	# write row metadata
	write_metadata(hdf5_out, "row", gctoo_object.row_metadata_df, convert_back_to_neg_666)

	# close gctx file 
	hdf5_out.close()

def add_gctx_to_out_name(out_file_name):
	"""
	If there isn't a '.gctx' suffix to specified out_file_name, it adds one.

	Input:
		- out_file_name (str): the file name to write gctx-formatted output to.
			(Can end with ".gctx" or not)

	Output:
		- out_file_name (str): the file name to write gctx-formatted output to, with ".gctx" suffix
	"""
	if not out_file_name.endswith(".gctx"):
		out_file_name = out_file_name + ".gctx"
	return out_file_name

def write_src(hdf5_out, gctoo_object, out_file_name):
	"""
	Writes src as attribute of gctx out file. 

	Input:
		- hdf5_out (h5py): hdf5 file to write to 
		- gctoo_object (GCToo): GCToo instance to be written to .gctx
		- out_file_name (str): name of hdf5 out file. 
	"""
	if gctoo_object.src == None:
		hdf5_out.attrs[src_attr] = out_file_name
	else:
		hdf5_out.attrs[src_attr] = gctoo_object.src

def write_version(hdf5_out):
	"""
	Writes version as attribute of gctx out file. 

	Input:
		- hdf5_out (h5py): hdf5 file to write to 
	"""
	hdf5_out.attrs[version_attr] = numpy.string_(version_number)

def write_metadata(hdf5_out, dim, metadata_df, convert_back_to_neg_666):
	"""
	Writes either column or row metadata to proper node of gctx out (hdf5) file.

	Input:
		- hdf5_out (h5py): open hdf5 file to write to
		- dim (str; must be "row" or "col"): dimension of metadata to write to 
		- metadata_df (pandas DataFrame): metadata DataFrame to write to file 
		- convert_back_to_neg_666 (bool): Whether to convert numpy.nans back to "-666",
				as per CMap metadata null convention 
	"""
	if dim == "col":
		hdf5_out.create_group(col_meta_group_node)
		metadata_node_name = col_meta_group_node
	elif dim == "row":
		hdf5_out.create_group(row_meta_group_node)
		metadata_node_name = row_meta_group_node
	else:
		logger.error("'dim' argument must be either 'row' or 'col'!")

	# write id field to expected node
	hdf5_out.create_dataset(metadata_node_name + "/id", data=list(metadata_df.index.copy()))

	metadata_fields = list(metadata_df.columns.copy())

	# if specified, convert numpy.nans in metadata back to -666
	if convert_back_to_neg_666:
		for c in metadata_fields:
			metadata_df[[c]] = metadata_df[[c]].replace([numpy.nan], ["-666"])

	# write metadata columns to their own arrays 
	for field in [entry for entry in metadata_fields if entry != "ind"]:
		hdf5_out.create_dataset(metadata_node_name + "/" + field, 
			data=numpy.array(list(metadata_df.loc[:,field])))


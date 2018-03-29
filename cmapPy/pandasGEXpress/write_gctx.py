import logging
import h5py
import numpy
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger

__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

logger = logging.getLogger(setup_logger.LOGGER_NAME)

src_attr = "src"
data_matrix_node = "/0/DATA/0/matrix"
row_meta_group_node = "/0/META/ROW"
col_meta_group_node = "/0/META/COL"
version_attr = "version"
version_number = "GCTX1.0"


def write(gctoo_object, out_file_name, convert_back_to_neg_666=True, gzip_compression_level=6,
    max_chunk_kb=1024, matrix_dtype=numpy.float32):
    """
	Writes a GCToo instance to specified file.

	Input:
		- gctoo_object (GCToo): A GCToo instance.
		- out_file_name (str): file name to write gctoo_object to.
        - convert_back_to_neg_666 (bool): whether to convert np.NAN in metadata back to "-666"
        - gzip_compression_level (int, default=6): Compression level to use for metadata. 
        - max_chunk_kb (int, default=1024): The maximum number of KB a given chunk will occupy
        - matrix_dtype (numpy dtype, default=numpy.float32): Storage data type for data matrix. 
	"""
    # make sure out file has a .gctx suffix
    gctx_out_name = add_gctx_to_out_name(out_file_name)

    # open an hdf5 file to write to
    hdf5_out = h5py.File(gctx_out_name, "w")

    # write version
    write_version(hdf5_out)

    # write src
    write_src(hdf5_out, gctoo_object, gctx_out_name)

    # set chunk size for data matrix
    elem_per_kb = calculate_elem_per_kb(max_chunk_kb, matrix_dtype)
    chunk_size = set_data_matrix_chunk_size(gctoo_object.data_df.shape, max_chunk_kb, elem_per_kb)

    # write data matrix
    hdf5_out.create_dataset(data_matrix_node, data=gctoo_object.data_df.transpose().as_matrix(), 
        dtype=matrix_dtype)

    # write col metadata
    write_metadata(hdf5_out, "col", gctoo_object.col_metadata_df, convert_back_to_neg_666, 
        gzip_compression=gzip_compression_level)

    # write row metadata
    write_metadata(hdf5_out, "row", gctoo_object.row_metadata_df, convert_back_to_neg_666,
        gzip_compression=gzip_compression_level)

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

def calculate_elem_per_kb(max_chunk_kb, matrix_dtype):
    """
    Calculates the number of elem per kb depending on the max chunk size set. 

    Input: 
        - max_chunk_kb (int, default=1024): The maximum number of KB a given chunk will occupy
        - matrix_dtype (numpy dtype, default=numpy.float32): Storage data type for data matrix. 
            Currently needs to be np.float32 or np.float64 (TODO: figure out a better way to get bits from a numpy dtype).

    Returns: 
        elem_per_kb (int), the number of elements per kb for matrix dtype specified. 
    """
    if matrix_dtype == numpy.float32:
        return (max_chunk_kb * 8)/32
    elif matrix_dtype == numpy.float64:
        return (max_chunk_kb * 8)/64
    else:
        msg = "Invalid matrix_dtype: {}; only numpy.float32 and numpy.float64 are currently supported".format(matrix_dtype)
        logger.error(msg)
        raise Exception("write_gctx.calculate_elem_per_kb " + msg)


def set_data_matrix_chunk_size(df_shape, max_chunk_kb, elem_per_kb):
    """
    Sets chunk size to use for writing data matrix. 
    Note. Calculation used here is for compatibility with cmapM and cmapR. 

    Input:
        - df_shape (tuple): shape of input data_df. 
        - max_chunk_kb (int, default=1024): The maximum number of KB a given chunk will occupy
        - elem_per_kb (int): Number of elements per kb 

    Returns:
        chunk size (tuple) to use for chunking the data matrix 
    """ 
    row_chunk_size = min(df_shape[0], 1000)
    col_chunk_size = min(((max_chunk_kb*elem_per_kb)//row_chunk_size), df_shape[1])
    return (row_chunk_size, col_chunk_size)

def write_metadata(hdf5_out, dim, metadata_df, convert_back_to_neg_666, gzip_compression):
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
    hdf5_out.create_dataset(metadata_node_name + "/id", data=[str(x) for x in metadata_df.index], 
        compression=gzip_compression)

    metadata_fields = list(metadata_df.columns.copy())

    # if specified, convert numpy.nans in metadata back to -666
    if convert_back_to_neg_666:
        for c in metadata_fields:
            metadata_df[[c]] = metadata_df[[c]].replace([numpy.nan], ["-666"])

    # write metadata columns to their own arrays
    for field in [entry for entry in metadata_fields if entry != "ind"]:
        hdf5_out.create_dataset(metadata_node_name + "/" + field,
                                data=numpy.array(list(metadata_df.loc[:, field])), 
                                compression=gzip_compression)

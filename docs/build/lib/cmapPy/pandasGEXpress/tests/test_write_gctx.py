import logging
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger
import unittest
import h5py
import os
import numpy
from cmapPy.pandasGEXpress import parse_gctx as parse_gctx
from cmapPy.pandasGEXpress import write_gctx as write_gctx
from cmapPy.pandasGEXpress import mini_gctoo_for_testing as mini_gctoo_for_testing

__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

FUNCTIONAL_TESTS_PATH = "functional_tests"

# instantiate logger
logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestWriteGctx(unittest.TestCase):

	def test_add_gctx_to_out_name(self):
		name1 = "my_cool_file"
		name2 = "my_other_cool_file.gctx"

		# case 1: out file name doesn't end in gctx
		out_name1 = write_gctx.add_gctx_to_out_name(name1)
		self.assertTrue(out_name1 == name1 + ".gctx", 
			("out name should be my_cool_file.gctx, not {}").format(out_name1))

		# case 2: out file name does end in gctx
		out_name2 = write_gctx.add_gctx_to_out_name(name2)
		self.assertTrue(out_name2 == name2,
			("out name should be my_other_cool_file.gctx, not {}").format(out_name2))

	def test_write_src(self):
		# case 1: gctoo obj doesn't have src
		mini1 = mini_gctoo_for_testing.make()
		mini1.src = None
		write_gctx.write(mini1, "no_src_example")
		hdf5_file = h5py.File("no_src_example.gctx")
		hdf5_src1 = hdf5_file.attrs[write_gctx.src_attr]
		hdf5_file.close()
		self.assertEqual(hdf5_src1, "no_src_example.gctx")
		os.remove("no_src_example.gctx")
		
		# case 2: gctoo obj does have src 
		mini2 = mini_gctoo_for_testing.make()
		write_gctx.write(mini2, "with_src_example.gctx")
		hdf5_file = h5py.File("with_src_example.gctx")
		hdf5_src2 = hdf5_file.attrs[write_gctx.src_attr]
		hdf5_file.close()
		self.assertEqual(hdf5_src2, "mini_gctoo.gctx")
		os.remove("with_src_example.gctx")

	def test_write_version(self):
		#TODO @oana refactor this test so it just calls the write_version method
		# case 1: gctoo obj doesn't have version
		mini1 = mini_gctoo_for_testing.make()
		mini1.version = None 
		fn = "no_version_provided_example.gctx"
		write_gctx.write(mini1, fn)
		hdf5_file = h5py.File(fn)
		hdf5_v1 = hdf5_file.attrs[write_gctx.version_attr]
		hdf5_file.close()
		self.assertEqual(hdf5_v1, write_gctx.version_number)
		os.remove(fn)

		# case 2: gctoo obj does have version, but it is not used when writing
		mini2 = mini_gctoo_for_testing.make()
		mini2.version = "MY_VERSION"
		fn = "with_version_provided_example.gctx"
		write_gctx.write(mini2, fn)
		hdf5_file = h5py.File(fn)
		hdf5_v2 = hdf5_file.attrs[write_gctx.version_attr]
		hdf5_file.close()
		self.assertEqual(hdf5_v2, write_gctx.version_number)
		os.remove(fn)

	def test_write_metadata(self):
		"""
		CASE 1:
			- write metadata (has '-666') to file, do not convert -666
			- parse in written metadata, don't convert -666 
		"""
		mini_gctoo = mini_gctoo_for_testing.make(convert_neg_666=False)
		hdf5_writer = h5py.File(FUNCTIONAL_TESTS_PATH + "/mini_gctoo_metadata.gctx", "w")
		write_gctx.write_metadata(hdf5_writer, "row", mini_gctoo.row_metadata_df, False)
		write_gctx.write_metadata(hdf5_writer, "col", mini_gctoo.col_metadata_df, False)
		hdf5_writer.close()
		logger.debug("Wrote mini_gctoo_metadata.gctx to {}".format(os.path.join(FUNCTIONAL_TESTS_PATH, "mini_gctoo_metadata.gctx")))

		# read in written metadata, then close and delete file
		mini_gctoo_col_metadata = parse_gctx.get_column_metadata(FUNCTIONAL_TESTS_PATH + "/mini_gctoo_metadata.gctx", convert_neg_666=False)
		mini_gctoo_row_metadata = parse_gctx.get_row_metadata(FUNCTIONAL_TESTS_PATH + "/mini_gctoo_metadata.gctx", convert_neg_666=False)

		os.remove(FUNCTIONAL_TESTS_PATH + "/mini_gctoo_metadata.gctx")

		# check row metadata
		self.assertTrue(set(mini_gctoo.row_metadata_df.columns) == set(mini_gctoo_row_metadata.columns),
			"Mismatch between expected row metadata columns {} and column values written to file: {}".format(mini_gctoo.row_metadata_df.columns, mini_gctoo_row_metadata.columns))
		self.assertTrue(set(mini_gctoo.row_metadata_df.index) == set(mini_gctoo.col_metadata_df.index),
			"Mismatch between expect row metadata index {} and index values written to file: {}".format(mini_gctoo.row_metadata_df.index, mini_gctoo_row_metadata.index))
		for c in list(mini_gctoo.row_metadata_df.columns):
			logger.debug("C1: For column name: {}".format(c))
			logger.debug("C1: populated values: {}".format(set(mini_gctoo_row_metadata[c])))
			logger.debug("C1: mini_gctoo values: {}".format(set(mini_gctoo.row_metadata_df[c])))
			self.assertTrue(set(mini_gctoo.row_metadata_df[c]) == set(mini_gctoo_row_metadata[c]), 
				"Values in column {} differ between expected metadata and written row metadata: {} vs {}".format(c, set(mini_gctoo.row_metadata_df[c]), set(mini_gctoo_row_metadata[c])))

		# check col metadata
		self.assertTrue(set(mini_gctoo.col_metadata_df.columns) == set(mini_gctoo_col_metadata.columns),
			"Mismatch between expected col metadata columns {} and column values written to file: {}".format(mini_gctoo.col_metadata_df.columns, mini_gctoo_col_metadata.columns))
		self.assertTrue(set(mini_gctoo.col_metadata_df.index) == set(mini_gctoo.col_metadata_df.index),
			"Mismatch between expect col metadata index {} and index values written to file: {}".format(mini_gctoo.col_metadata_df.index, mini_gctoo_col_metadata.index))
		for c in list(mini_gctoo.col_metadata_df.columns):
			self.assertTrue(set(mini_gctoo.col_metadata_df[c]) == set(mini_gctoo_col_metadata[c]), 
				"Values in column {} differ between expected metadata and written col metadata!".format(c))

		"""
		CASE 2:
			- write metadata (has NaN, not '-666') to file, do convert NaN back to '-666'
			- parse in written metadata, don't convert -666 
		"""
		# first convert mini_gctoo's row & col metadata dfs -666s to NaN
		converted_row_metadata = mini_gctoo.row_metadata_df.replace([-666, "-666", -666.0], [numpy.nan, numpy.nan, numpy.nan])
		logger.debug("First row of converted_row_metadata: {}".format(converted_row_metadata.iloc[0]))
		converted_col_metadata = mini_gctoo.col_metadata_df.replace([-666, "-666", -666.0], [numpy.nan, numpy.nan, numpy.nan])

		# write row and col metadata fields from mini_gctoo_for_testing instance to file
		# Note this time does convert back to -666
		hdf5_writer = h5py.File(FUNCTIONAL_TESTS_PATH + "/mini_gctoo_metadata.gctx", "w")
		write_gctx.write_metadata(hdf5_writer, "row", converted_row_metadata, True)
		write_gctx.write_metadata(hdf5_writer, "col", converted_col_metadata, True)
		hdf5_writer.close()

		# read in written metadata, then close and delete file
		mini_gctoo_col_metadata = parse_gctx.get_column_metadata(FUNCTIONAL_TESTS_PATH + "/mini_gctoo_metadata.gctx", convert_neg_666=False)
		mini_gctoo_row_metadata = parse_gctx.get_row_metadata(FUNCTIONAL_TESTS_PATH + "/mini_gctoo_metadata.gctx", convert_neg_666=False)


		os.remove(FUNCTIONAL_TESTS_PATH + "/mini_gctoo_metadata.gctx")

		# check row metadata
		self.assertTrue(set(mini_gctoo.row_metadata_df.columns) == set(mini_gctoo_row_metadata.columns),
			"Mismatch between expected row metadata columns {} and column values written to file: {}".format(mini_gctoo.row_metadata_df.columns, mini_gctoo_row_metadata.columns))
		self.assertTrue(set(mini_gctoo.row_metadata_df.index) == set(mini_gctoo.col_metadata_df.index),
			"Mismatch between expect row metadata index {} and index values written to file: {}".format(mini_gctoo.row_metadata_df.index, mini_gctoo_row_metadata.index))
		for c in list(mini_gctoo.row_metadata_df.columns):
			logger.debug("C2: For column name: {}".format(c))
			logger.debug("C2: populated values: {}".format(set(mini_gctoo_row_metadata[c])))
			logger.debug("C2: mini_gctoo values: {}".format(set(mini_gctoo.row_metadata_df[c])))
			self.assertTrue(set(mini_gctoo.row_metadata_df[c]) == set(mini_gctoo_row_metadata[c]), 
				"Values in column {} differ between expected metadata and written row metadata!".format(c))

		# check col metadata
		self.assertTrue(set(mini_gctoo.col_metadata_df.columns) == set(mini_gctoo_col_metadata.columns),
			"Mismatch between expected col metadata columns {} and column values written to file: {}".format(mini_gctoo.col_metadata_df.columns, mini_gctoo_col_metadata.columns))
		self.assertTrue(set(mini_gctoo.col_metadata_df.index) == set(mini_gctoo.col_metadata_df.index),
			"Mismatch between expect col metadata index {} and index values written to file: {}".format(mini_gctoo.col_metadata_df.index, mini_gctoo_col_metadata.index))
		for c in list(mini_gctoo.col_metadata_df.columns):
			self.assertTrue(set(mini_gctoo.col_metadata_df[c]) == set(mini_gctoo_col_metadata[c]), 
				"Values in column {} differ between expected metadata and written col metadata!".format(c))

if __name__ == "__main__":
	setup_logger.setup(verbose=True)
	
	unittest.main()

"""
Functional tests comparing gct vs gctx parsing for equivalent file content 
(stored in gct/text vs gctx/hdf5 format)
"""

import unittest
import logging
import pandas
import numpy
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger
from cmapPy.pandasGEXpress import parse_gct as parse_gct
from cmapPy.pandasGEXpress import parse_gctx as parse_gctx 
from pandas.util.testing import assert_series_equal

FUNCTIONAL_TESTS_PATH = "functional_tests"

logger = logging.getLogger(setup_logger.LOGGER_NAME)

class TestEdgeCases(unittest.TestCase):

	###### parsing case 1: Both col & row metadata ######
	def test_with_both_metadata_fields(self):

		# path to files
		gctoo_path = FUNCTIONAL_TESTS_PATH + "/both_metadata_example_n1476x978.gct"
		gctoox_path = FUNCTIONAL_TESTS_PATH + "/both_metadata_example_n1476x978.gctx"

		# parse files
		c1_gctoo = parse_gct.parse(gctoo_path)
		c1_gctoox = parse_gctx.parse(gctoox_path)

		#check rows and columns: data_df
		self.assertTrue(set(list(c1_gctoo.data_df.index)) == set(list(c1_gctoox.data_df.index)),
			"Mismatch between data_df index values of gct vs gctx: {} vs {}".format(c1_gctoo.data_df.index, c1_gctoox.data_df.index))
		self.assertTrue(set(list(c1_gctoo.data_df.columns)) == set(list(c1_gctoox.data_df.columns)),
			"Mismatch between data_df column values of gct vs gctx: {} vs {}".format(c1_gctoo.data_df.columns, c1_gctoox.data_df.columns))
		logger.debug("c1 gctoo data_df columns equal to gctoox data_df columns? {}".format(set(c1_gctoo.data_df.columns) == set(c1_gctoox.data_df.columns)))
		for c in list(c1_gctoo.data_df.columns):
			# logger.debug("Comparing data values in Column: {}".format(c))
			self.assertTrue(len(list(c1_gctoo.data_df[c])) == len(list(c1_gctoox.data_df[c])),
				"Lengths of column {} differ between gct and gctx".format(c))
			# assert_frame_equal(pandas.DataFrame(c1_gctoo.data_df[c]), pandas.DataFrame(c1_gctoox.data_df[c]))
			assert_series_equal(c1_gctoo.data_df[c], c1_gctoox.data_df[c])

		# check rows and columns: row_metadata_df
		self.assertTrue(set(list(c1_gctoo.row_metadata_df.index)) == set(list(c1_gctoox.row_metadata_df.index)),
			"Mismatch between row_metadata_df index values of gct vs gctx: {} vs {}".format(c1_gctoo.row_metadata_df.index, c1_gctoox.row_metadata_df.index))
		self.assertTrue(set(list(c1_gctoo.row_metadata_df.columns)) == set(list(c1_gctoox.row_metadata_df.columns)),
			"Mismatch between row_metadata_df column values of gct vs gctx: difference is {}".format(set(c1_gctoo.row_metadata_df.columns).symmetric_difference(set(c1_gctoox.row_metadata_df.columns))))
		logger.debug("c1 gctoo row_metadata_df columns equal to gctoox row_metadata_df columns? {}".format(set(c1_gctoo.row_metadata_df.columns) == set(c1_gctoox.row_metadata_df.columns)))
		logger.debug("c1 gctoo dtypes: {}".format(c1_gctoo.row_metadata_df.dtypes))
		logger.debug("c1 gctoox dtypes: {}".format(c1_gctoox.row_metadata_df.dtypes))
		for c in list(c1_gctoo.row_metadata_df.columns):
			self.assertTrue(len(list(c1_gctoo.row_metadata_df[c])) == len(list(c1_gctoox.row_metadata_df[c])),
				"Lengths of column {} differ between gct and gctx".format(c))
			logger.debug("first couple elems of {} in gctoo: {}".format(c, list(c1_gctoo.row_metadata_df[c])[0:3]))
			self.assertTrue(c1_gctoo.row_metadata_df[c].dtype == c1_gctoox.row_metadata_df[c].dtype,
				"Dtype mismatch for {} between parsed gct & gctx: {} vs {}".format(c, c1_gctoo.row_metadata_df[c].dtype, c1_gctoox.row_metadata_df[c].dtype))
			assert_series_equal(c1_gctoo.row_metadata_df[c], c1_gctoox.row_metadata_df[c])

		# check rows and columns: col_metadata_df
		self.assertTrue(set(list(c1_gctoo.col_metadata_df.index)) == set(list(c1_gctoox.col_metadata_df.index)),
			"Mismatch between col_metadata_df index values of gct vs gctx: {} vs {}".format(c1_gctoo.col_metadata_df.index, c1_gctoox.col_metadata_df.index))
		self.assertTrue(set(list(c1_gctoo.col_metadata_df.columns)) == set(list(c1_gctoox.col_metadata_df.columns)),
			"Mismatch between col_metadata_df column values of gct vs gctx: {} vs {}".format(c1_gctoo.col_metadata_df.columns, c1_gctoox.col_metadata_df.columns))
		logger.debug("c1 gctoo col_metadata_df columns equal to gctoox col_metadata_df columns? {}".format(set(c1_gctoo.col_metadata_df.columns) == set(c1_gctoox.col_metadata_df.columns)))
		for c in list(c1_gctoo.col_metadata_df.columns):
			self.assertTrue(len(list(c1_gctoo.col_metadata_df[c])) == len(list(c1_gctoox.col_metadata_df[c])),
				"Lengths of column {} differ between gct and gctx".format(c))
			self.assertTrue(c1_gctoo.col_metadata_df[c].dtype == c1_gctoox.col_metadata_df[c].dtype,
				"Dtype mismatch between parsed gct & gctx: {} vs {}".format(c1_gctoo.col_metadata_df[c].dtype, c1_gctoox.col_metadata_df[c].dtype))

			assert_series_equal(c1_gctoo.col_metadata_df[c], c1_gctoox.col_metadata_df[c])

	# # ###### parsing case 2: Only row metadata ######
	def test_with_only_row_metadata(self):
		
		# path to files
		gctoo_path = FUNCTIONAL_TESTS_PATH + "/row_meta_only_example_n2x1203.gct"
		gctoox_path = FUNCTIONAL_TESTS_PATH + "/row_meta_only_example_n2x1203.gctx"

		# parse files
		c2_gctoo = parse_gct.parse(gctoo_path)
		c2_gctoox = parse_gctx.parse(gctoox_path)

		#check rows and columns: data_df
		self.assertTrue(set(list(c2_gctoo.data_df.index)) == set(list(c2_gctoox.data_df.index)),
			"Mismatch between data_df index values of gct vs gctx: {} vs {}".format(c2_gctoo.data_df.index, c2_gctoox.data_df.index))
		self.assertTrue(set(list(c2_gctoo.data_df.columns)) == set(list(c2_gctoox.data_df.columns)),
			"Mismatch between data_df column values of gct vs gctx: {} vs {}".format(c2_gctoo.data_df.columns, c2_gctoox.data_df.columns))
		logger.debug("c2 gctoo data_df columns equal to gctoox data_df columns? {}".format(set(c2_gctoo.data_df.columns) == set(c2_gctoox.data_df.columns)))
		for c in list(c2_gctoo.data_df.columns):
			self.assertTrue(len(list(c2_gctoo.data_df[c])) == len(list(c2_gctoox.data_df[c])),
				"Lengths of column {} differ between gct and gctx".format(c))
			assert_series_equal(c2_gctoo.data_df[c], c2_gctoox.data_df[c])

		# check rows and columns: row_metadata_df
		self.assertTrue(set(list(c2_gctoo.row_metadata_df.index)) == set(list(c2_gctoox.row_metadata_df.index)),
			"Mismatch between row_metadata_df index values of gct vs gctx: {} vs {}".format(c2_gctoo.row_metadata_df.index, c2_gctoox.row_metadata_df.index))
		self.assertTrue(set(list(c2_gctoo.row_metadata_df.columns)) == set(list(c2_gctoox.row_metadata_df.columns)),
			"Mismatch between row_metadata_df column values of gct vs gctx: {} vs {}".format(c2_gctoo.row_metadata_df.columns, c2_gctoox.row_metadata_df.columns))
		logger.debug("c2 gctoo row_metadata_df columns equal to gctoox row_metadata_df columns? {}".format(set(c2_gctoo.row_metadata_df.columns) == set(c2_gctoox.row_metadata_df.columns)))
		for c in list(c2_gctoo.row_metadata_df.columns):
			self.assertTrue(len(list(c2_gctoo.row_metadata_df[c])) == len(list(c2_gctoox.row_metadata_df[c])),
				"Lengths of column {} differ between gct and gctx".format(c))
			self.assertTrue(c2_gctoo.row_metadata_df[c].dtype == c2_gctoox.row_metadata_df[c].dtype,
				"Dtype mismatch between parsed gct & gctx: {} vs {}".format(c2_gctoo.row_metadata_df[c].dtype, c2_gctoox.row_metadata_df[c].dtype))
			logger.debug("first couple elems of {} in gctoo: {}".format(c, list(c2_gctoo.row_metadata_df[c])[0:3]))
			assert_series_equal(c2_gctoo.row_metadata_df[c], c2_gctoox.row_metadata_df[c])

		# check rows and columns: col_metadata_df
		self.assertTrue(set(list(c2_gctoo.col_metadata_df.index)) == set(list(c2_gctoox.col_metadata_df.index)),
			"Mismatch between col_metadata_df index values of gct vs gctx: {} vs {}".format(c2_gctoo.col_metadata_df.index, c2_gctoox.col_metadata_df.index))
		self.assertTrue(set(list(c2_gctoo.col_metadata_df.columns)) == set(list(c2_gctoox.col_metadata_df.columns)),
			"Mismatch between col_metadata_df column values of gct vs gctx: {} vs {}".format(c2_gctoo.col_metadata_df.columns, c2_gctoox.col_metadata_df.columns))
		logger.debug("c2 gctoo col_metadata_df columns equal to gctoox col_metadata_df columns? {}".format(set(c2_gctoo.col_metadata_df.columns) == set(c2_gctoox.col_metadata_df.columns)))
		for c in list(c2_gctoo.col_metadata_df.columns):
			self.assertTrue(len(list(c2_gctoo.col_metadata_df[c])) == len(list(c2_gctoox.col_metadata_df[c])),
				"Lengths of column {} differ between gct and gctx".format(c))
			self.assertTrue(c2_gctoo.col_metadata_df[c].dtype == c2_gctoox.col_metadata_df[c].dtype,
				"Dtype mismatch between parsed gct & gctx: {} vs {}".format(c2_gctoo.col_metadata_df[c].dtype, c2_gctoox.col_metadata_df[c].dtype))
			assert_series_equal(c2_gctoo.col_metadata_df[c], c2_gctoox.col_metadata_df[c])

	# # ###### parsing case 3: Only col metadata ######
	def test_with_only_col_metadata(self):

		# path to files
		gctoo_path = FUNCTIONAL_TESTS_PATH + "/col_meta_only_example_n355x355.gct"
		gctoox_path = FUNCTIONAL_TESTS_PATH + "/col_meta_only_example_n355x355.gctx"

				# parse files
		c3_gctoo = parse_gct.parse(gctoo_path)
		c3_gctoox = parse_gctx.parse(gctoox_path)

		#check rows and columns: data_df
		self.assertTrue(set(list(c3_gctoo.data_df.index)) == set(list(c3_gctoox.data_df.index)),
			"Mismatch between data_df index values of gct vs gctx: {} vs {}".format(c3_gctoo.data_df.index, c3_gctoox.data_df.index))
		self.assertTrue(set(list(c3_gctoo.data_df.columns)) == set(list(c3_gctoox.data_df.columns)),
			"Mismatch between data_df column values of gct vs gctx: {} vs {}".format(c3_gctoo.data_df.columns, c3_gctoox.data_df.columns))
		logger.debug("c3 gctoo data_df columns equal to gctoox data_df columns? {}".format(set(c3_gctoo.data_df.columns) == set(c3_gctoox.data_df.columns)))
		for c in list(c3_gctoo.data_df.columns):
			self.assertTrue(len(list(c3_gctoo.data_df[c])) == len(list(c3_gctoox.data_df[c])),
				"Lengths of column {} differ between gct and gctx".format(c))
			assert_series_equal(c3_gctoo.data_df[c], c3_gctoox.data_df[c])

		# check rows and columns: row_metadata_df
		self.assertTrue(set(list(c3_gctoo.row_metadata_df.index)) == set(list(c3_gctoox.row_metadata_df.index)),
			"Mismatch between row_metadata_df index values of gct vs gctx: {} vs {}".format(c3_gctoo.row_metadata_df.index, c3_gctoox.row_metadata_df.index))
		self.assertTrue(set(list(c3_gctoo.row_metadata_df.columns)) == set(list(c3_gctoox.row_metadata_df.columns)),
			"Mismatch between row_metadata_df column values of gct vs gctx: {} vs {}".format(c3_gctoo.row_metadata_df.columns, c3_gctoox.row_metadata_df.columns))
		logger.debug("c3 gctoo row_metadata_df columns equal to gctoox row_metadata_df columns? {}".format(set(c3_gctoo.row_metadata_df.columns) == set(c3_gctoox.row_metadata_df.columns)))
		for c in list(c3_gctoo.row_metadata_df.columns):
			self.assertTrue(len(list(c3_gctoo.row_metadata_df[c])) == len(list(c3_gctoox.row_metadata_df[c])),
				"Lengths of column {} differ between gct and gctx".format(c))
			self.assertTrue(c3_gctoo.row_metadata_df[c].dtype == c3_gctoox.row_metadata_df[c].dtype,
				"Dtype mismatch between parsed gct & gctx: {} vs {}".format(c3_gctoo.row_metadata_df[c].dtype, c3_gctoox.row_metadata_df[c].dtype))
			logger.debug("first couple elems of {} in gctoo: {}".format(c, list(c3_gctoo.row_metadata_df[c])[0:3]))
			assert_series_equal(c3_gctoo.row_metadata_df[c], c3_gctoox.row_metadata_df[c])

		# check rows and columns: col_metadata_df
		self.assertTrue(set(list(c3_gctoo.col_metadata_df.index)) == set(list(c3_gctoox.col_metadata_df.index)),
			"Mismatch between col_metadata_df index values of gct vs gctx: {} vs {}".format(c3_gctoo.col_metadata_df.index, c3_gctoox.col_metadata_df.index))
		self.assertTrue(set(list(c3_gctoo.col_metadata_df.columns)) == set(list(c3_gctoox.col_metadata_df.columns)),
			"Mismatch between col_metadata_df column values of gct vs gctx: {} vs {}".format(c3_gctoo.col_metadata_df.columns, c3_gctoox.col_metadata_df.columns))
		logger.debug("c3 gctoo col_metadata_df columns equal to gctoox col_metadata_df columns? {}".format(set(c3_gctoo.col_metadata_df.columns) == set(c3_gctoox.col_metadata_df.columns)))
		for c in list(c3_gctoo.col_metadata_df.columns):
			self.assertTrue(len(list(c3_gctoo.col_metadata_df[c])) == len(list(c3_gctoox.col_metadata_df[c])),
				"Lengths of column {} differ between gct and gctx".format(c))
			self.assertTrue(c3_gctoo.col_metadata_df[c].dtype == c3_gctoox.col_metadata_df[c].dtype,
				"Dtype mismatch between parsed gct & gctx: {} vs {}".format(c3_gctoo.col_metadata_df[c].dtype, c3_gctoox.col_metadata_df[c].dtype))
			assert_series_equal(c3_gctoo.col_metadata_df[c], c3_gctoox.col_metadata_df[c])

if __name__ == "__main__":
	setup_logger.setup(verbose=True)

	unittest.main()
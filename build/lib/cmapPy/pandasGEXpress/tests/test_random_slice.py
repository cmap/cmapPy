import unittest
import logging
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger
from cmapPy.pandasGEXpress import random_slice as random_slice
from cmapPy.pandasGEXpress import mini_gctoo_for_testing as mini_gctoo_for_testing


logger = logging.getLogger(setup_logger.LOGGER_NAME)

class TestRandomSlice(unittest.TestCase):
	def test_make_specified_size_gctoo(self):
		mini_gctoo = mini_gctoo_for_testing.make()
		logger.debug("mini gctoo data_df shape: {}".format(mini_gctoo.data_df.shape))
		logger.debug("mini gctoo row_meta shape: {}".format(mini_gctoo.row_metadata_df.shape))
		logger.debug("mini gctoo col_meta shape: {}".format(mini_gctoo.col_metadata_df.shape))

		# case 1: dim isn't 'row' or 'col'
		with self.assertRaises(AssertionError) as context:
			random_slice.make_specified_size_gctoo(mini_gctoo, 3, "aaaalll")
		self.assertEqual(str(context.exception), "dim specified must be either 'row' or 'col'")

		# case 2: row subsetting - happy
		row_subset = random_slice.make_specified_size_gctoo(mini_gctoo, 3, "row")
		self.assertEqual(row_subset.data_df.shape, (3,6), 
			"data_df after row slice is incorrect shape: {} vs (3,6)".format(row_subset.data_df.shape))
		self.assertEqual(row_subset.row_metadata_df.shape, (3,5), 
			"row_metadata_df after row slice is incorrect shape: {} vs (3,5)".format(row_subset.row_metadata_df.shape))
		self.assertEqual(row_subset.col_metadata_df.shape, (6,5),
			"col_metadata_df after row slice is incorrect shape: {} vs (6,5)".format(row_subset.col_metadata_df.shape))

		# case 3: row subsetting - sample subset > og # of samples
		with self.assertRaises(AssertionError) as context:
			random_slice.make_specified_size_gctoo(mini_gctoo, 30, "row")
		self.assertTrue("number of entries must be smaller than dimension being subsetted " in str(context.exception))

		# case 4: col subsetting - happy
		col_subset = random_slice.make_specified_size_gctoo(mini_gctoo, 3, "col")
		self.assertEqual(col_subset.data_df.shape, (6,3), 
			"data_df after col slice is incorrect shape: {} vs (6,3)".format(col_subset.data_df.shape))
		self.assertEqual(col_subset.row_metadata_df.shape, (6, 5), 
			"row_metadata_df after col slice is incorrect shape: {} vs (6, 5)".format(col_subset.row_metadata_df.shape))
		self.assertEqual(col_subset.col_metadata_df.shape, (3,5),
			"col_metadata_df after col slice is incorrect shape: {} vs (3,5)".format(col_subset.col_metadata_df.shape))

		# case 5: col subsetting - sample subset > og # of samples
		with self.assertRaises(AssertionError) as context:
			random_slice.make_specified_size_gctoo(mini_gctoo, 7, "col")
		self.assertTrue("number of entries must be smaller than dimension being subsetted " in str(context.exception))

if __name__ == "__main__":
	
	setup_logger.setup(verbose=True)

	unittest.main()

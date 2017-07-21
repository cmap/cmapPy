import logging
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger
import unittest
import os
import pandas as pd
import numpy as np
from cmapPy.pandasGEXpress import GCToo
import h5py
from cmapPy.pandasGEXpress import parse_gctx as parse_gctx
from cmapPy.pandasGEXpress import mini_gctoo_for_testing as mini_gctoo_for_testing
from cmapPy.pandasGEXpress import slice_gct as slice_gct
from cmapPy.pandasGEXpress import write_gctx as write_gctx 
from pandas.util.testing import assert_frame_equal

__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

FUNCTIONAL_TESTS_PATH = "functional_tests"

logger = logging.getLogger(setup_logger.LOGGER_NAME)

version_node = "version"
rid_node = "/0/META/ROW/id"
cid_node = "/0/META/COL/id"
data_node = "/0/DATA/0/matrix"
row_meta_group_node = "/0/META/ROW"
col_meta_group_node = "/0/META/COL"

class TestParseGctx(unittest.TestCase):
	def test_parse(self):
		# parse whole thing 
		mg1 = mini_gctoo_for_testing.make()
		mg2 = parse_gctx.parse("functional_tests/mini_gctoo_for_testing.gctx")

		assert_frame_equal(mg1.data_df, mg2.data_df)
		assert_frame_equal(mg1.row_metadata_df, mg2.row_metadata_df)
		assert_frame_equal(mg1.col_metadata_df, mg2.col_metadata_df)

		# test with string rid/cid 
		test_rids = ['LJP007_MCF10A_24H:TRT_CP:BRD-K93918653:3.33','LJP007_MCF7_24H:CTL_VEHICLE:DMSO:-666']
		test_cids = ['LJP007_MCF7_24H:TRT_POSCON:BRD-A61304759:10']
		mg3 = slice_gct.slice_gctoo(mg1, rid=test_rids, cid=test_cids)
		mg4 = parse_gctx.parse("functional_tests/mini_gctoo_for_testing.gctx",
			rid = test_rids, cid = test_cids)
		assert_frame_equal(mg3.data_df, mg4.data_df)
		assert_frame_equal(mg3.row_metadata_df, mg4.row_metadata_df)
		assert_frame_equal(mg3.col_metadata_df, mg4.col_metadata_df)

		# first, make & write out temp version of mini_gctoo with int rids/cids 
		new_mg = mini_gctoo_for_testing.make(convert_neg_666=False)
		int_indexed_data_df = new_mg.data_df.copy()
		int_indexed_data_df.index = range(0,6)
		int_indexed_data_df.columns = range(10,16)

		int_indexed_row_meta = new_mg.row_metadata_df.copy()
		int_indexed_row_meta.index = range(0,6)

		int_indexed_col_meta = new_mg.col_metadata_df.copy()
		int_indexed_col_meta.index = range(10,16)

		int_indexed_gctoo = GCToo.GCToo(data_df = int_indexed_data_df, row_metadata_df = int_indexed_row_meta,
			col_metadata_df = int_indexed_col_meta)

		write_gctx.write(int_indexed_gctoo, "int_indexed_mini_gctoo.gctx")

		# test with numeric (repr as string) rid/cid
		mg5 = GCToo.GCToo(data_df = int_indexed_data_df, row_metadata_df = int_indexed_row_meta, 
			col_metadata_df = int_indexed_col_meta)
		mg5 = slice_gct.slice_gctoo(mg5, row_bool = [True, False, True, False, True, False],
			col_bool = [True, False, False, True, True, True])

		mg5.data_df.index.name = "rid"
		mg5.data_df.columns.name = "cid"

		mg5.row_metadata_df.index.name = "rid"
		mg5.row_metadata_df.columns.name = "rhd"

		mg5.col_metadata_df.index.name = "cid"
		mg5.col_metadata_df.columns.name = "chd"

		mg6 = parse_gctx.parse("int_indexed_mini_gctoo.gctx", rid = [0, 2, 4], 
			cid = [10,13,14,15], convert_neg_666=False)

		os.remove("int_indexed_mini_gctoo.gctx")

		assert_frame_equal(mg5.data_df, mg6.data_df)
		assert_frame_equal(mg5.row_metadata_df, mg6.row_metadata_df)
		assert_frame_equal(mg5.col_metadata_df, mg6.col_metadata_df)		

		# test with ridx/cidx
		mg7 = slice_gct.slice_gctoo(mg1, rid=['LJP007_MCF7_24H:CTL_VEHICLE:DMSO:-666'], 
			cid='LJP007_MCF7_24H:CTL_VEHICLE:DMSO:-666')
		mg8 = parse_gctx.parse("functional_tests/mini_gctoo_for_testing.gctx", ridx=[4], cidx=[4])

		assert_frame_equal(mg7.data_df, mg8.data_df)
		assert_frame_equal(mg7.row_metadata_df, mg8.row_metadata_df)
		assert_frame_equal(mg7.col_metadata_df, mg8.col_metadata_df)			

		# test with rid/cidx
		mg9 = parse_gctx.parse("functional_tests/mini_gctoo_for_testing.gctx", rid=['LJP007_MCF7_24H:CTL_VEHICLE:DMSO:-666'],
			cidx = [4])

		assert_frame_equal(mg7.data_df, mg9.data_df)
		assert_frame_equal(mg7.row_metadata_df, mg9.row_metadata_df)
		assert_frame_equal(mg7.col_metadata_df, mg9.col_metadata_df)			

		# test with ridx/cid
		mg10 = parse_gctx.parse("functional_tests/mini_gctoo_for_testing.gctx", ridx=[4],
			cid = ['LJP007_MCF7_24H:CTL_VEHICLE:DMSO:-666'])

		assert_frame_equal(mg7.data_df, mg10.data_df)
		assert_frame_equal(mg7.row_metadata_df, mg10.row_metadata_df)
		assert_frame_equal(mg7.col_metadata_df, mg10.col_metadata_df)	

		# test with row_meta_only 
		mg11 = parse_gctx.parse("functional_tests/mini_gctoo_for_testing.gctx", row_meta_only=True)
		assert_frame_equal(mg11, mg1.row_metadata_df)

		# test with col_meta_only
		mg12 = parse_gctx.parse("functional_tests/mini_gctoo_for_testing.gctx", col_meta_only=True)
		assert_frame_equal(mg12, mg1.col_metadata_df)		

	def test_parse_rid_as_entrez_id(self):
		input_file = "functional_tests/test_parse_gctx_rid_entrez_id.gctx"
		g = parse_gctx.parse(input_file)
		self.assertEqual((5,5), g.data_df.shape)
		logger.debug("g.data_df.index:  {}".format(g.data_df.index))

		my_rids = [5720, 55847, 7416]
		g = parse_gctx.parse(input_file, rid=my_rids)
		self.assertEqual((3,5), g.data_df.shape)
		logger.debug("g.data_df.index:  {}".format(g.data_df.index))

		my_rids = [str(x) for x in my_rids]
		logger.debug("using rid as str (mismatched type) - my_rids:  {}".format(my_rids))
		g = parse_gctx.parse(input_file, rid=my_rids)
		self.assertEqual((3,5), g.data_df.shape)
		logger.debug("g.data_df.index:  {}".format(g.data_df.index))

	def test_check_and_order_id_inputs(self):
		ridx = [0,1]
		cidx = [2,1]
		rid = ["a", "b", "c"]
		cid = ["l", "m", "n", "o"]
		row_meta = pd.DataFrame(index=["b", "c", "a", "d"])
		col_meta = pd.DataFrame(index=["l", "m", "n", "o", "p", "q"])

		# case 1: row and col lists are populated and same type
		self.assertEqual((sorted(ridx), sorted(cidx)), 
			parse_gctx.check_and_order_id_inputs(None, ridx, None, cidx, row_meta, col_meta))

		# case 2: row & col lists are populated, but of different types
		self.assertEqual((sorted(ridx), [0,1,2,3]), 
			parse_gctx.check_and_order_id_inputs(None,ridx, cid, None, row_meta, col_meta))

		# case 3: row list and col lists are both None 
		self.assertEqual(([0,1,2,3], [0,1,2,3,4,5]), 
			parse_gctx.check_and_order_id_inputs(None, None, None, None, row_meta, col_meta))

		# case 4: row list is populated, col list is None 
		self.assertEqual(([0,1,2], [0,1,2,3,4,5]), 
			parse_gctx.check_and_order_id_inputs(rid, None, None, None, row_meta, col_meta))

	def test_check_id_idx_exclusivity(self):
		ids = ["a", "b", "c"]
		idx = [0, 1, 2]

		# case 1: id != None and idx != None
		with self.assertRaises(Exception) as context:
			parse_gctx.check_id_idx_exclusivity(ids, idx)
		self.assertTrue("'id' and 'idx' fields can't both not be None" in str(context.exception))

		# case 2: id != None
		self.assertEqual(("id", ids), parse_gctx.check_id_idx_exclusivity(ids, None))

		# case 3: idx != None
		self.assertEqual(("idx", idx), parse_gctx.check_id_idx_exclusivity(None, idx))

		# case 4: id == None & idx == None 	
		self.assertEqual((None, []), parse_gctx.check_id_idx_exclusivity(None, None))	

	def test_parse_metadata_df(self):
		mini_gctoo = mini_gctoo_for_testing.make()
		# convert row_metadata to np.nan
		mini_row_meta = mini_gctoo.row_metadata_df.replace([-666, "-666", -666.0], [np.nan, np.nan, np.nan])

		gctx_file = h5py.File("functional_tests/mini_gctoo_for_testing.gctx", "r")
		row_dset = gctx_file[row_meta_group_node]
		col_dset = gctx_file[col_meta_group_node]

		# with convert_neg_666
		row_df = parse_gctx.parse_metadata_df("row", row_dset, True)
		assert_frame_equal(mini_row_meta, row_df)

		# no convert_neg_666
		mini_gctoo_with_neg_666 = mini_gctoo_for_testing.make(convert_neg_666=False)
		col_df = parse_gctx.parse_metadata_df("col", col_dset, False)
		assert_frame_equal(mini_gctoo_with_neg_666.col_metadata_df, col_df)

	def test_replace_666(self):
		# convert_neg_666 is True
		row_df = pd.DataFrame([[3, "a"], [-666, "c"], ["-666", -666.0]],
							  index=["r1", "r2", "r3"], columns=["rhd1", "rhd2"])
		e_df = pd.DataFrame([[3, "a"], [np.nan, "c"], [np.nan, np.nan]],
							  index=["r1", "r2", "r3"], columns=["rhd1", "rhd2"])
		out_df = parse_gctx.replace_666(row_df, convert_neg_666=True)
		self.assertTrue(e_df.equals(out_df))

		# convert_neg_666 is False
		e_df2 = pd.DataFrame([[3, "a"], ["-666", "c"], ["-666", "-666"]],
							  index=["r1", "r2", "r3"], columns=["rhd1", "rhd2"])
		out_df2 = parse_gctx.replace_666(row_df, convert_neg_666=False)
		self.assertTrue(e_df2.equals(out_df2))

		# edge case: if row meta is 1 column of floats
		row_df3 = pd.DataFrame([[3], [-666], [-666.0]],
							   index=["r1", "r2", "r3"], columns=["rhd3"])
		e_df3 = pd.DataFrame([[3], [np.nan], [np.nan]],
							   index=["r1", "r2", "r3"], columns=["rhd3"])
		out_df3 = parse_gctx.replace_666(row_df3, convert_neg_666=True)
		self.assertTrue(e_df3.equals(out_df3))

	def test_set_metadata_index_and_column_names(self):
		mini_gctoo = mini_gctoo_for_testing.make()
		mini_gctoo.row_metadata_df.index.name = None
		mini_gctoo.row_metadata_df.columns.name = None 
		mini_gctoo.col_metadata_df.index.name = None
		mini_gctoo.col_metadata_df.columns.name = None 

		# case 1: dim == "row"
		parse_gctx.set_metadata_index_and_column_names("row", mini_gctoo.row_metadata_df)
		self.assertEqual(mini_gctoo.row_metadata_df.index.name, "rid")
		self.assertEqual(mini_gctoo.row_metadata_df.columns.name, "rhd")

		# case 2: dim == "col"
		parse_gctx.set_metadata_index_and_column_names("col", mini_gctoo.col_metadata_df)
		self.assertEqual(mini_gctoo.col_metadata_df.index.name, "cid")
		self.assertEqual(mini_gctoo.col_metadata_df.columns.name, "chd")

	def test_get_ordered_idx(self):
		mg = mini_gctoo_for_testing.make()

		# case 1: id_type == None
		case1 = parse_gctx.get_ordered_idx(None, [], mg.row_metadata_df)
		self.assertEqual(case1, range(0,6), 
			"Expected oredered idx to be {} but got {}".format(range(0,6), case1))

		# case 2: id_type == "id"
		case2 = parse_gctx.get_ordered_idx("id", 
			['LJP007_MCF7_24H:CTL_VEHICLE:DMSO:-666'], mg.col_metadata_df)
		self.assertEqual(case2, [4], 
			"Expected oredered idx to be {} but got {}".format([4], case2))

		# case 3: id_type == ridx 
		case3 = parse_gctx.get_ordered_idx("idx", 
			[5,1,3], mg.col_metadata_df)
		self.assertEqual(case3, [1,3,5], 
			"Expected oredered idx to be {} but got {}".format([1,3,5], case3))		

	def test_parse_data_df(self):
		mini_data_df = pd.DataFrame([[-0.283359, 0.011270],[0.304119, 1.921061],[0.398655, -0.144652]], 
			index=["200814_at", "218597_s_at", "217140_s_at"], 
			columns = ["LJP005_A375_24H:DMSO:-666", "LJP005_A375_24H:BRD-K76908866:10"])
		mini_data_df = mini_data_df.astype(np.float32)
		mini_data_df.index.name = "rid"
		mini_data_df.columns.name = "cid"

		# create h5py File instance 
		mini_gctx = h5py.File("functional_tests/mini_gctx_with_metadata_n2x3.gctx", "r")
		data_dset = mini_gctx[data_node]

		# get relevant metadata fields
		col_meta = parse_gctx.get_column_metadata("functional_tests/mini_gctx_with_metadata_n2x3.gctx")
		row_meta = parse_gctx.get_row_metadata("functional_tests/mini_gctx_with_metadata_n2x3.gctx")

		# case 1: no slicing
		data_df1 = parse_gctx.parse_data_df(data_dset, [0,1,2], [0,1], row_meta, col_meta)
		# note: checks to 3 decimal places 
		assert_frame_equal(mini_data_df, data_df1, 
			check_exact=False, check_less_precise = True)

		# case 2: slice; ridx < cidx 
		data_df2 = parse_gctx.parse_data_df(data_dset, [0], [0,1], row_meta, col_meta)
		assert_frame_equal(mini_data_df.iloc[[0],[0,1]], data_df2, 
			check_exact=False, check_less_precise = True)

		# case 3: slice; ridx == cidx 
		data_df3 = parse_gctx.parse_data_df(data_dset, [0],[0], row_meta, col_meta)
		assert_frame_equal(mini_data_df.iloc[[0],[0]], data_df3, 
			check_exact=False, check_less_precise = True)

		# case 4: slice; ridx > cidx 
		data_df4 = parse_gctx.parse_data_df(data_dset, [0,1,2],[0], row_meta, col_meta)
		assert_frame_equal(mini_data_df.iloc[[0,1,2],[0]], data_df4, 
			check_exact=False, check_less_precise = True)
	
		mini_gctx.close()

	def test_convert_ids_to_meta_type(self):
		#happy path
		id_list = range(3)
		self.assertEqual(int, type(id_list[0]))
		df = pd.DataFrame({}, index=pd.Series(range(1,4)).astype(np.int64))
		r = parse_gctx.convert_ids_to_meta_type(id_list, df)
		logger.debug("conversion from regular int to numpy int64 - type(r[0]):  {}".format(type(r[0])))
		self.assertEqual(np.int64, type(r[0]))

		id_list = [str(i) for i in xrange(3)]
		r = parse_gctx.convert_ids_to_meta_type(id_list, df)
		logger.debug("conversion from str to numpy int64 - type(r[0]):  {}".format(type(r[0])))
		self.assertEqual(np.int64, type(r[0]))

		#unhappy path 
		id_list[0] = "a"
		with self.assertRaises(Exception) as context:
			parse_gctx.convert_ids_to_meta_type(id_list, df)
		logger.debug("context.exception:  {}".format(context.exception))
		self.assertIn("The type of the id_list (rid or cid) being used to subset the data is not compatible with the metadata id's in the file",
			str(context.exception))

	def test_check_idx_validity(self):
		id_list = range(3)
		df = pd.DataFrame({}, index=range(5))
		logger.debug("df.shape:  {}".format(df.shape))
		parse_gctx.check_idx_validity(id_list, df)

		id_list[0] = -1
		with self.assertRaises(Exception) as context:
			parse_gctx.check_idx_validity(id_list, df)
		logger.debug("context.exception:  {}".format(context.exception))
		self.assertIn("some of indexes being used to subset the data are not valid", str(context.exception))
		self.assertIn("[-1]", str(context.exception))

		invalid_high = df.shape[0] + 1
		id_list[0] = invalid_high
		with self.assertRaises(Exception) as context:
			parse_gctx.check_idx_validity(id_list, df)
		logger.debug("context.exception:  {}".format(context.exception))
		self.assertIn("some of indexes being used to subset the data are not valid", str(context.exception))
		self.assertIn("[{}]".format(invalid_high), str(context.exception))

	def test_check_id_validity(self):
		id_list = ["a", "b", "c"]
		df = pd.DataFrame({}, index=["a", "b", "c", "d"])
		parse_gctx.check_id_validity(id_list, df)
		
		id_list[0] = "z"
		with self.assertRaises(Exception) as context:
			parse_gctx.check_id_validity(id_list, df)
		logger.debug("context.exception:  {}".format(context.exception))
		self.assertIn("some of the ids being used to subset the data are not present in the metadata for the file being parsed",
			str(context.exception))


if __name__ == "__main__":
	setup_logger.setup(verbose=True)

	unittest.main()

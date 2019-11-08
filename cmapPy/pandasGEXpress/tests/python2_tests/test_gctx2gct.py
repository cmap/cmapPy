import unittest
import logging
import pandas as pd
import os
import cmapPy.pandasGEXpress.gctx2gct as gctx2gct
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.parse_gct as parse_gct
import cmapPy.pandasGEXpress.parse_gctx as parse_gctx

logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestGCTx2GCT(unittest.TestCase):

	def test_gctx2gct_main(self):

		in_name = "cmapPy/pandasGEXpress/tests/functional_tests//mini_gctoo_for_testing.gctx"
		out_name = "cmapPy/pandasGEXpress/tests/functional_tests//test_gctx2gct_out.gct"
		args_string = "-f {} -o {}".format(in_name, out_name)
		args = gctx2gct.build_parser().parse_args(args_string.split())

		gctx2gct.gctx2gct_main(args)

		# Make sure the input is identical to output
		in_gctx = parse_gctx.parse(in_name)
		out_gct = parse_gct.parse(out_name)

		pd.util.testing.assert_frame_equal(in_gctx.data_df, out_gct.data_df, check_less_precise=3)
		pd.util.testing.assert_frame_equal(in_gctx.col_metadata_df, out_gct.col_metadata_df)
		pd.util.testing.assert_frame_equal(in_gctx.row_metadata_df, out_gct.row_metadata_df)

		no_meta = "cmapPy/pandasGEXpress/tests/functional_tests//mini_gctoo_for_testing_nometa.gctx"
		added_meta = "cmapPy/pandasGEXpress/tests/functional_tests//test_gctx2gct_out_annotated.gct"
		row_meta = "cmapPy/pandasGEXpress/tests/functional_tests//test_rowmeta_n6.txt"
		col_meta = "cmapPy/pandasGEXpress/tests/functional_tests//test_colmeta_n6.txt"
		args_string = "-f {} -o {} -row_annot_path {} -col_annot_path {}".format(no_meta, added_meta, row_meta, col_meta )
		args = gctx2gct.build_parser().parse_args(args_string.split())

		gctx2gct.gctx2gct_main(args)

		annotated_gct = parse_gct.parse(added_meta)

		# Check added annotations are the same as original input GCTX
		pd.util.testing.assert_frame_equal(in_gctx.data_df, annotated_gct.data_df, check_less_precise=3)
		pd.util.testing.assert_frame_equal(in_gctx.col_metadata_df, annotated_gct.col_metadata_df)
		pd.util.testing.assert_frame_equal(in_gctx.row_metadata_df, annotated_gct.row_metadata_df)

		# Clean up
		os.remove(out_name)
		os.remove(added_meta)

	def test_missing_annotations(self):
		with self.assertRaises(Exception) as context:
			no_meta = "cmapPy/pandasGEXpress/tests/functional_tests//mini_gctoo_for_testing_nometa.gctx"
			added_meta = "cmapPy/pandasGEXpress/tests/functional_tests//test_gctx2gct_out_annotated.gct"
			row_meta = "cmapPy/pandasGEXpress/tests/functional_tests//test_missing_rowmeta.txt"
			args_string = "-f {} -o {} -row_annot_path {}".format(no_meta, added_meta, row_meta)
			args = gctx2gct.build_parser().parse_args(args_string.split())

			gctx2gct.gctx2gct_main(args)

		self.assertTrue('Row ids in matrix missing from annotations file' in context.exception)

		with self.assertRaises(Exception) as context:
			no_meta = "cmapPy/pandasGEXpress/tests/functional_tests//mini_gctoo_for_testing_nometa.gctx"
			added_meta = "cmapPy/pandasGEXpress/tests/functional_tests//test_gctx2gct_out_annotated.gct"
			col_meta = "cmapPy/pandasGEXpress/tests/functional_tests//test_missing_colmeta.txt"
			args_string = "-f {} -o {} -col_annot_path {}".format(no_meta, added_meta, col_meta)
			args = gctx2gct.build_parser().parse_args(args_string.split())

			gctx2gct.gctx2gct_main(args)

		self.assertTrue('Column ids in matrix missing from annotations file' in context.exception)


if __name__ == "__main__":
	setup_logger.setup(verbose=True)
	unittest.main()

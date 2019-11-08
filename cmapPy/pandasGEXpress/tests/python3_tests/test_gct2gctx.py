import unittest
import logging
import pandas as pd
import os
import cmapPy.pandasGEXpress.gct2gctx as gct2gctx
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.parse_gct as parse_gct
import cmapPy.pandasGEXpress.parse_gctx as parse_gctx

logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestGCT2GCTx(unittest.TestCase):

	def test_gct2gctx_main(self):

		in_name = "cmapPy/pandasGEXpress/tests/functional_tests/mini_gctoo_for_testing.gct"
		out_name = "cmapPy/pandasGEXpress/tests/functional_tests/test_gct2gctx_out.gctx"
		args_string = "-f {} -o {}".format(in_name, out_name)
		args = gct2gctx.build_parser().parse_args(args_string.split())

		gct2gctx.gct2gctx_main(args)

		# Make sure the input is identical to output
		in_gct = parse_gct.parse(in_name)
		out_gctx = parse_gctx.parse(out_name)

		pd.util.testing.assert_frame_equal(in_gct.data_df, out_gctx.data_df)
		pd.util.testing.assert_frame_equal(in_gct.col_metadata_df, out_gctx.col_metadata_df)
		pd.util.testing.assert_frame_equal(in_gct.row_metadata_df, out_gctx.row_metadata_df)

		no_meta = "cmapPy/pandasGEXpress/tests/functional_tests/mini_gctoo_for_testing_nometa.gct"
		added_meta = "cmapPy/pandasGEXpress/tests/functional_tests/test_gct2gctx_out_annotated.gctx"
		row_meta = "cmapPy/pandasGEXpress/tests/functional_tests/test_rowmeta_n6.txt"
		col_meta = "cmapPy/pandasGEXpress/tests/functional_tests/test_colmeta_n6.txt"
		args_string = "-f {} -o {} -row_annot_path {} -col_annot_path {}".format(no_meta, added_meta, row_meta, col_meta)
		args = gct2gctx.build_parser().parse_args(args_string.split())

		gct2gctx.gct2gctx_main(args)

		annotated_gctx = parse_gctx.parse(added_meta)

		# Check added annotations are the same as original input GCTX
		pd.util.testing.assert_frame_equal(in_gct.data_df, annotated_gctx.data_df, check_less_precise=3)
		pd.util.testing.assert_frame_equal(in_gct.col_metadata_df, annotated_gctx.col_metadata_df)
		pd.util.testing.assert_frame_equal(in_gct.row_metadata_df, annotated_gctx.row_metadata_df)

		# Clean up
		os.remove(out_name)
		os.remove(added_meta)

	def test_missing_annotations(self):
		with self.assertRaises(Exception) as context:
			no_meta = "../functional_tests/mini_gctoo_for_testing_nometa.gct"
			added_meta = "../functional_tests/test_gctx2gct_out_annotated.gctx"
			row_meta = "../functional_tests/test_missing_rowmeta.txt"
			args_string = "-f {} -o {} -row_annot_path {}".format(no_meta, added_meta, row_meta)
			args = gct2gctx.build_parser().parse_args(args_string.split())

			gct2gctx.gct2gctx_main(args)

		self.assertTrue('Row ids in matrix missing from annotations file', context.exception)

		with self.assertRaises(Exception) as context:
			no_meta = "../functional_tests/mini_gctoo_for_testing_nometa.gct"
			added_meta = "../functional_tests/test_gctx2gct_out_annotated.gctx"
			col_meta = "../functional_tests/test_missing_colmeta.txt"
			args_string = "-f {} -o {} -col_annot_path {}".format(no_meta, added_meta, col_meta)
			args = gct2gctx.build_parser().parse_args(args_string.split())

			gct2gctx.gct2gctx_main(args)

		self.assertTrue('Column ids in matrix missing from annotations file', context.exception)


if __name__ == "__main__":
	setup_logger.setup(verbose=True)
	unittest.main()

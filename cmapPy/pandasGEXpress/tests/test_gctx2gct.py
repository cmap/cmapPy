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

		in_name = "functional_tests/mini_gctoo_for_testing.gctx"
		out_name = "functional_tests/test_gctx2gct_out.gct"
		args_string = "-f {} -o {}".format(in_name, out_name)
		args = gctx2gct.build_parser().parse_args(args_string.split())

		gctx2gct.gctx2gct_main(args)

		# Make sure the input is identical to output
		in_gctx = parse_gctx.parse(in_name)
		out_gct = parse_gct.parse(out_name)

		pd.util.testing.assert_frame_equal(in_gctx.data_df, out_gct.data_df, check_less_precise=3)
		pd.util.testing.assert_frame_equal(in_gctx.col_metadata_df, out_gct.col_metadata_df)
		pd.util.testing.assert_frame_equal(in_gctx.row_metadata_df, out_gct.row_metadata_df)

		# Clean up
		os.remove(out_name)

if __name__ == "__main__":
	setup_logger.setup(verbose=True)
	unittest.main()

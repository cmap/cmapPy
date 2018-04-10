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

		in_name = "functional_tests/mini_gctoo_for_testing.gct"
		out_name = "functional_tests/test_gct2gctx_out.gctx"
		args_string = "-f {} -o {}".format(in_name, out_name)
		args = gct2gctx.build_parser().parse_args(args_string.split())

		gct2gctx.gct2gctx_main(args)

		# Make sure the input is identical to output
		in_gct = parse_gct.parse(in_name)
		out_gctx = parse_gctx.parse(out_name)

		pd.util.testing.assert_frame_equal(in_gct.data_df, out_gctx.data_df)
		pd.util.testing.assert_frame_equal(in_gct.col_metadata_df, out_gctx.col_metadata_df)
		pd.util.testing.assert_frame_equal(in_gct.row_metadata_df, out_gctx.row_metadata_df)

		# Clean up
		os.remove(out_name)

if __name__ == "__main__":
	setup_logger.setup(verbose=True)
	unittest.main()

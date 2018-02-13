import unittest
import logging
import os
import pandas as pd
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.parse as parse
import cmapPy.pandasGEXpress.slice_gct as slice_gct

logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestSliceGct(unittest.TestCase):

    def test_read_arg(self):
        arg_path = os.path.join("functional_tests", "test_slice_rid.grp")
        rids = slice_gct._read_arg([arg_path])
        self.assertItemsEqual(rids, ["a", "Bb", "c"])

    def test_read_arg_bad(self):
        with self.assertRaises(AssertionError) as e:
            slice_gct._read_arg("a b c")
        self.assertIn("arg_out must be a list", str(e.exception))

        with self.assertRaises(AssertionError) as e:
            slice_gct._read_arg([1, 2, 3])
        self.assertIn("arg_out must be a list of strings", str(e.exception))

    def test_main(self):

        in_gct_path = os.path.join("functional_tests", "test_slice_in.gct")
        rid_grp_path = os.path.join("functional_tests", "test_slice_rid.grp")
        out_name = os.path.join("functional_tests", "test_slice_out.gct")
        expected_out_path = os.path.join("functional_tests", "test_slice_expected.gct")

        # Use Mock object since main doesn't take args
        save_build_parser = slice_gct.build_parser

        class MockParser:
            def __init__(self, args):
                self.args = args

            def parse_args(self, unused):
                return self.args

        args_string = "-i {} --rid {} -ec {} -o {}".format(
            in_gct_path, rid_grp_path, "f", out_name)
        args = save_build_parser().parse_args(args_string.split())
        my_mock_parser = MockParser(args)
        slice_gct.build_parser = lambda: my_mock_parser

        # Run main method
        slice_gct.main()

        # Compare output to expected
        out_gct = parse.parse(out_name)
        expected_gct = parse.parse(expected_out_path)

        pd.util.testing.assert_frame_equal(out_gct.data_df, expected_gct.data_df)
        pd.util.testing.assert_frame_equal(out_gct.row_metadata_df, expected_gct.row_metadata_df)
        pd.util.testing.assert_frame_equal(out_gct.col_metadata_df, expected_gct.col_metadata_df)

        # Clean up
        os.remove(out_name)

if __name__ == '__main__':
    unittest.main()

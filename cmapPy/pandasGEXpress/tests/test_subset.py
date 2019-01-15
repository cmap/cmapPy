import unittest
import logging
import os
import pandas as pd
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.parse as parse
import cmapPy.pandasGEXpress.subset as sg

logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestSubset(unittest.TestCase):

    def test_read_arg(self):
        arg_path = os.path.join("functional_tests", "test_subset_rid.grp")
        rids = sg._read_arg([arg_path])
        self.assertItemsEqual(rids, ["a", "Bb", "c"])

    def test_read_arg_bad(self):
        with self.assertRaises(AssertionError) as e:
            sg._read_arg("a b c")
        self.assertIn("arg_out must be a list", str(e.exception))

        with self.assertRaises(AssertionError) as e:
            sg._read_arg([1, 2, 3])
        self.assertIn("arg_out must be a list of strings", str(e.exception))

    def test_subset_main(self):

        in_gct_path = os.path.join("functional_tests", "test_subset_in.gct")
        rid_grp_path = os.path.join("functional_tests", "test_subset_rid.grp")
        out_name = os.path.join("functional_tests", "test_subset_out.gct")
        expected_out_path = os.path.join("functional_tests", "test_subset_expected.gct")

        args_string = "-i {} --rid {} -ec {} -o {}".format(
            in_gct_path, rid_grp_path, "f", out_name)
        args = sg.build_parser().parse_args(args_string.split())

        # Run main method
        sg.subset_main(args)

        # Compare output to expected
        out_gct = parse.parse(out_name)
        expected_gct = parse.parse(expected_out_path)

        pd.util.testing.assert_frame_equal(out_gct.data_df, expected_gct.data_df)
        pd.util.testing.assert_frame_equal(out_gct.row_metadata_df, expected_gct.row_metadata_df)
        pd.util.testing.assert_frame_equal(out_gct.col_metadata_df, expected_gct.col_metadata_df)

        # Clean up
        os.remove(out_name)

        # gctx with exclude_rid should fail
        args_string2 = "-i {} --rid {} -ec {} -o {}".format(
            "FAKE.gctx", rid_grp_path, "f", out_name)
        args2 = sg.build_parser().parse_args(args_string2.split())

        with self.assertRaises(Exception) as e:
            sg.subset_main(args2)
        self.assertIn("exclude_{rid,cid} args not currently supported",
                      str(e.exception))

if __name__ == '__main__':
    unittest.main()

import os
import unittest
import logging
import numpy as np
import pandas as pd

from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger
from cmapPy.pandasGEXpress import concat_gctoo as cg
from cmapPy.pandasGEXpress import parse_gct as pg

logger = logging.getLogger(setup_logger.LOGGER_NAME)
FUNCTIONAL_TESTS_DIR = "functional_tests"


class TestConcatGctoo(unittest.TestCase):
    def test_left_right(self):
        left_gct_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_merge_left.gct")
        right_gct_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_merge_right.gct")
        expected_gct_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_merged_left_right.gct")

        left_gct = pg.parse(left_gct_path)
        right_gct = pg.parse(right_gct_path)
        expected_gct = pg.parse(expected_gct_path)

        # Merge left and right
        concated_gct = cg.hstack([left_gct, right_gct], [], False)

        pd.util.testing.assert_frame_equal(expected_gct.data_df, concated_gct.data_df, check_names=False)
        pd.util.testing.assert_frame_equal(expected_gct.row_metadata_df, concated_gct.row_metadata_df, check_names=False)
        pd.util.testing.assert_frame_equal(expected_gct.col_metadata_df, concated_gct.col_metadata_df, check_names=False)

    def test_top_bottom(self):
        top_gct_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_merge_top.gct")
        bottom_gct_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_merge_bottom.gct")
        expected_gct_path = os.path.join(FUNCTIONAL_TESTS_DIR, "test_merged_top_bottom.gct")

        top_gct = pg.parse(top_gct_path)
        bottom_gct = pg.parse(bottom_gct_path)
        expected_gct = pg.parse(expected_gct_path)

        # Merge top and bottom
        concated_gct = cg.vstack([top_gct, bottom_gct], [], False)

        pd.util.testing.assert_frame_equal(expected_gct.data_df, concated_gct.data_df, check_names=False)
        pd.util.testing.assert_frame_equal(expected_gct.row_metadata_df, concated_gct.row_metadata_df, check_names=False)
        pd.util.testing.assert_frame_equal(expected_gct.col_metadata_df, concated_gct.col_metadata_df, check_names=False)

    def test_assemble_common_meta(self):
        # rhd3 header needs to be removed
        meta1 = pd.DataFrame(
            [["r1_1", "r1_2", "r1_3"],
             ["r2_1", "r2_2", "r2_3"],
             ["r3_1", "r3_2", "r3_3"]],
            index=["r1", "r2", "r3"],
            columns=["rhd1", "rhd2", "rhd3"])
        meta2 = pd.DataFrame(
            [["r1_1", "r1_2", "r1_3"],
             ["r2_1", "r2_2", "r2_3"],
             ["r3_1", "r3_2", "r3_33"]],
            index=["r1", "r2", "r3"],
            columns=["rhd1", "rhd2", "rhd3"])
        e_meta1 = pd.DataFrame(
            [["r1_1", "r1_2"],
             ["r2_1", "r2_2"],
             ["r3_1", "r3_2"]],
            index=["r1", "r2", "r3"],
            columns=["rhd1", "rhd2"])

        logger.debug("meta1:\n{}".format(meta1))
        logger.debug("meta2:\n{}".format(meta2))
        logger.debug("e_meta:\n{}".format(e_meta1))

        with self.assertRaises(AssertionError) as e:
            _ = cg.assemble_common_meta([meta1.copy(), meta2.copy()], [])
        self.assertIn("r3", str(e.exception))
	logger.debug("rhd3 header needs to be removed - e.exception:  {}".format(e.exception))

        out_meta1 = cg.assemble_common_meta([meta1.copy(), meta2.copy()], ["rhd3"])
        logger.debug("out_meta1:\n{}".format(out_meta1))
        pd.util.testing.assert_frame_equal(out_meta1, e_meta1)

        # Order of indices and columns are different
        meta3 = pd.DataFrame(
            [["r3_1", "r3_3", "r3_2"],
             ["r1_1", "r1_3", "r1_2"],
             ["r2_1", "r2_3", "r2_2"]],
            index=["r3", "r1", "r2"],
            columns=["rhd1", "rhd3", "rhd2"])
        e_meta2 = pd.DataFrame(
            [["r1_1", "r1_2", "r1_3"],
             ["r2_1", "r2_2", "r2_3"],
             ["r3_1", "r3_2", "r3_3"]],
            index=["r1", "r2", "r3"],
            columns=["rhd1", "rhd2", "rhd3"])

        logger.debug("meta3:\n{}".format(meta3))
        logger.debug("e_meta2:\n{}".format(e_meta2))
        out_meta2 = cg.assemble_common_meta([meta1.copy(), meta3.copy()], [])
        pd.util.testing.assert_frame_equal(out_meta2, e_meta2)

        # Some ids not present in both dfs
        meta4 = pd.DataFrame(
            [["r1_1", "r1_22", "r1_5"],
             ["r4_1", "r4_22", "r4_5"],
             ["r3_1", "r3_22", "r3_5"]],
            index=["r1", "r4", "r3"],
            columns=["rhd1", "rhd2", "rhd5"])
        e_meta3 = pd.DataFrame(
            [["r1_1"],
             ["r2_1"],
             ["r3_1"],
             ["r4_1"]],
            index=["r1", "r2", "r3", "r4"],
            columns=["rhd1"])

        logger.debug("meta1:\n{}".format(meta1))
        logger.debug("meta4:\n{}".format(meta4))
        logger.debug("e_meta3:\n{}".format(e_meta3))

        with self.assertRaises(AssertionError) as e:
            _ = cg.assemble_common_meta([meta1.copy(), meta4.copy()], [])
        self.assertIn("r1", str(e.exception))

        out_meta3 = cg.assemble_common_meta([meta1.copy(), meta4.copy()], ["rhd2"])
        logger.debug("out_meta3:\n{}".format(out_meta3))
        pd.util.testing.assert_frame_equal(out_meta3, e_meta3)

        # Empty metadata
        empty_meta = pd.DataFrame([], index=["a", "b", "c"])
        logger.debug("empty_meta.empty: {}".format(empty_meta.empty))
        out_meta4 = cg.assemble_common_meta([empty_meta, empty_meta], [])
        pd.util.testing.assert_frame_equal(out_meta4, empty_meta)

        #metadata has duplicates but index is unique
        meta5 = pd.DataFrame({"rhd1":[0,0,1]}, index=range(3))
        meta6 = pd.DataFrame({"rhd1":[0,0,1]}, index=range(3))
        out_meta5 = cg.assemble_common_meta([meta5, meta6], [])
        self.assertEqual((3,1), out_meta5.shape)

    def test_assemble_concatenated_meta(self):
        # Happy path
        meta1 = pd.DataFrame(
            [["a", "b"], ["c", "d"]],
            index=["c1", "c2"],
            columns=["hd1", "hd2"])
        meta2 = pd.DataFrame(
            [["e", "f", "g"], ["h", "i", "j"]],
            index=["c2", "c3"],
            columns=["hd1", "hd2", "hd3"])
        e_concated = pd.DataFrame(
            [["a", "b", np.nan], ["e", "f", "g"],
             ["c", "d", np.nan], ["h", "i", "j"]],
            index=["c1", "c2", "c2", "c3"],
            columns=["hd1", "hd2", "hd3"])

        logger.debug("meta1:\n{}".format(meta1))
        logger.debug("meta2:\n{}".format(meta2))
        logger.debug("e_concated:\n{}".format(e_concated))

        concated = cg.assemble_concatenated_meta([meta2, meta1])
        pd.util.testing.assert_frame_equal(e_concated, concated)

    def test_assemble_data(self):
        # Horizontal concat
        df1 = pd.DataFrame(
            [[1, 2, 3], [4, 5, 6]],
            index=["a", "b"],
            columns=["s1", "s2", "s3"])
        df2 = pd.DataFrame(
            [[10, 11, 12], [7, 8, 9]],
            index=["b", "a"],
            columns=["s4", "s5", "s6"])
        e_horiz_concated = pd.DataFrame(
            [[1, 2, 3, 7, 8, 9], [4, 5, 6, 10, 11, 12]],
            index=["a", "b"],
            columns=["s1", "s2", "s3", "s4", "s5", "s6"])

        horiz_concated = cg.assemble_data([df1, df2], "horiz")
        pd.util.testing.assert_frame_equal(horiz_concated, e_horiz_concated)

        # Vertical concat, df3 has s4 instead of s3
        df3 = pd.DataFrame(
            [[8, 2, 5], [-1, 2, 4]],
            index=["c", "e"],
            columns=["s1", "s2", "s4"])
        e_vert_concated = pd.DataFrame(
            [[1, 2, 3, np.nan], [4, 5, 6, np.nan],
             [8, 2, np.nan, 5], [-1, 2, np.nan, 4]],
            index=["a", "b", "c", "e"],
            columns=["s1", "s2", "s3", "s4"])

        vert_concated = cg.assemble_data([df3, df1], "vert")
        pd.util.testing.assert_frame_equal(vert_concated, e_vert_concated)

    def test_do_reset_ids(self):
        meta_df = pd.DataFrame(
            [[1, 2], [3, 4], [5, 6]],
            index=["s1", "s2", "s1"],
            columns=["hd1", "hd2"])
        data_df = pd.DataFrame(
            [[1, 2, 3], [4, 5, 6]],
            index=["a", "b"],
            columns=["s1", "s2", "s1"])
        inconsistent_data_df = pd.DataFrame(
            [[1, 2, 3], [4, 5, 6]],
            index=["a", "b"],
            columns=["s1", "s2", "s3"])
        e_meta_df = pd.DataFrame(
            [["s1", 1, 2], ["s2", 3, 4], ["s1", 5, 6]],
            index=[0, 1, 2],
            columns=["old_id", "hd1", "hd2"])
        e_data_df = pd.DataFrame(
            [[1, 2, 3], [4, 5, 6]],
            index=["a", "b"],
            columns=[0, 1, 2])

        # Check the assert statement
        with self.assertRaises(AssertionError) as e:
            cg.do_reset_ids(meta_df.copy(), inconsistent_data_df, "horiz")
        self.assertIn("do not agree with cids", str(e.exception))

        # Happy path
        cg.do_reset_ids(meta_df, data_df, "horiz")
        pd.util.testing.assert_frame_equal(meta_df, e_meta_df)
        pd.util.testing.assert_frame_equal(data_df, e_data_df)

if __name__ == "__main__":
    setup_logger.setup(verbose=True)

    unittest.main()

import unittest
import logging
import pandas as pd
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.GCToo as GCToo
import cmapPy.pandasGEXpress.slice_gctoo as sg


logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestSliceGCToo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_df = pd.DataFrame([[1, 2, 3], [5, 7, 11], [13, 17, 19], [23, 29, 31]],
                               index=["a", "b", "c", "d"], columns=["e", "f", "g"])
        row_metadata_df = pd.DataFrame([["rm1", "rm2"], ["rm3", "rm4"], ["rm5", "rm6"], ["rm7", "rm8"]],
                                       index=["a","b","c","d"], columns=["rhd1", "rh2"])
        col_metadata_df = pd.DataFrame([["cm1", "cm2"], ["cm3", "cm4"], ["cm5", "cm6"]],
                                       index=["e", "f", "g"], columns=["chd1", "chd2"])
        cls.in_gct = GCToo.GCToo(data_df, row_metadata_df, col_metadata_df)

    def test_slice_bools(self):
        out_gct = sg.slice_gctoo(self.in_gct, row_bool=[True, False, True, False], col_bool=[False, False, True])

        # Outputs should be dataframes even if there is only 1 index or column
        pd.util.testing.assert_frame_equal(out_gct.data_df, pd.DataFrame(self.in_gct.data_df.iloc[[0, 2], 2]))
        pd.util.testing.assert_frame_equal(out_gct.row_metadata_df, self.in_gct.row_metadata_df.iloc[[0, 2], :])
        pd.util.testing.assert_frame_equal(out_gct.col_metadata_df, pd.DataFrame(self.in_gct.col_metadata_df.iloc[2, :]).T)

    def test_slice_and_exclude_rids(self):
        out_gct = sg.slice_gctoo(self.in_gct, rid=["a", "c", "d"], exclude_rid=["d"])

        # Outputs should be dataframes even if there is only 1 index or column
        pd.util.testing.assert_frame_equal(out_gct.data_df, self.in_gct.data_df.iloc[[0, 2], :])
        pd.util.testing.assert_frame_equal(out_gct.row_metadata_df, self.in_gct.row_metadata_df.iloc[[0, 2], :])
        pd.util.testing.assert_frame_equal(out_gct.col_metadata_df, self.in_gct.col_metadata_df)

    def test_slice_cid_and_col_bool(self):
        # cid and col_bool should not both be provided
        with self.assertRaises(AssertionError) as e:
            sg.slice_gctoo(self.in_gct, cid=["e", "f", "g"], col_bool=[True, True, False])
        self.assertIn("cid and col_bool", str(e.exception))


if __name__ == '__main__':
    setup_logger.setup(verbose=True)
    unittest.main()

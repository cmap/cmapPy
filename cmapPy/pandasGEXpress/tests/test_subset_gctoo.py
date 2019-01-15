import unittest
import logging
import pandas as pd
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.GCToo as GCToo
import cmapPy.pandasGEXpress.subset_gctoo as sg


logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestSubsetGCToo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        data_df = pd.DataFrame([[1, 2, 3], [5, 7, 11], [13, 17, 19], [23, 29, 31]],
                               index=["a", "b", "c", "d"], columns=["e", "f", "g"])
        row_metadata_df = pd.DataFrame([["rm1", "rm2"], ["rm3", "rm4"], ["rm5", "rm6"], ["rm7", "rm8"]],
                                       index=["a", "b", "c", "d"], columns=["rhd1", "rh2"])
        col_metadata_df = pd.DataFrame([["cm1", "cm2"], ["cm3", "cm4"], ["cm5", "cm6"]],
                                       index=["e", "f", "g"], columns=["chd1", "chd2"])
        cls.in_gct = GCToo.GCToo(data_df, row_metadata_df, col_metadata_df)

    def test_subset_gctoo(self):

        # Error if resulting GCT is empty
        with self.assertRaises(AssertionError) as e:
            sg.subset_gctoo(self.in_gct, rid=["bad"], cid=["x", "y"])
        self.assertIn("Subsetting yielded an", str(e.exception))

        # cid and col_bool should not both be provided
        with self.assertRaises(AssertionError) as e:
            sg.subset_gctoo(self.in_gct, cid=["e", "f", "g"], col_bool=[True, True, False])
        self.assertIn("Only one of cid,", str(e.exception))

        # Providing all 3 row inputs is also bad!
        with self.assertRaises(AssertionError) as e:
            sg.subset_gctoo(self.in_gct, rid="blah", ridx="bloop", row_bool="no!")
        self.assertIn("Only one of rid,", str(e.exception))

        # happy path
        out_g = sg.subset_gctoo(self.in_gct, rid=["d", "a", "b"], cidx=[0],
                               exclude_rid=["a"])
        pd.util.testing.assert_frame_equal(out_g.data_df, self.in_gct.data_df.iloc[[1, 3], [0]])

    def test_get_rows_to_keep(self):

        # rid must be a list
        with self.assertRaises(AssertionError) as e:
            sg.get_rows_to_keep(self.in_gct, rid="bad")
        self.assertIn("rid must be a list", str(e.exception))

        # bools
        out_rows = sg.get_rows_to_keep(self.in_gct, row_bool=[True, True, True, False])
        self.assertItemsEqual(out_rows, ["a", "b", "c"])

        # rid and exclude_rid
        out_rows2 = sg.get_rows_to_keep(self.in_gct, rid=["a", "c", "d"], exclude_rid=["d"])
        self.assertItemsEqual(out_rows2, ["a", "c"])

        # keep all rows
        out_rows3 = sg.get_rows_to_keep(self.in_gct)
        self.assertItemsEqual(out_rows3, ["a", "b", "c", "d"])

        with self.assertRaises(AssertionError) as e:
            sg.get_rows_to_keep(self.in_gct, row_bool=[True, False, True])
        self.assertIn("row_bool must have length", str(e.exception))

        with self.assertRaises(AssertionError) as e:
            sg.get_rows_to_keep(self.in_gct, ridx=[True, False, True])
        self.assertIn("ridx must be a list of integers", str(e.exception))

        with self.assertRaises(AssertionError) as e:
            sg.get_rows_to_keep(self.in_gct, ridx=[0, 2, 5])
        self.assertIn("ridx contains an integer", str(e.exception))

    def test_get_cols_to_keep(self):
        # N.B. annoying that we have two extremely similar but separate methods
        # for rows and columns, but I think it's worth it to have clear error
        # messages

        # cid must be a list
        with self.assertRaises(AssertionError) as e:
            sg.get_cols_to_keep(self.in_gct, cid="real_bad")
        self.assertIn("cid must be a list", str(e.exception))

        # bools
        out_cols = sg.get_cols_to_keep(self.in_gct, col_bool=[False, True, True])
        self.assertItemsEqual(out_cols, ["f", "g"])

        # cid and exclude_cid
        out_cols2 = sg.get_cols_to_keep(self.in_gct, cid=["g", "e", "f"], exclude_cid=["f"], cidx=None)
        self.assertItemsEqual(out_cols2, ["g", "e"])

        # keep all cols
        out_cols3 = sg.get_cols_to_keep(self.in_gct)
        self.assertItemsEqual(out_cols3, ["e", "f", "g"])

        with self.assertRaises(AssertionError) as e:
            sg.get_cols_to_keep(self.in_gct, col_bool=[True, False, True, True])
        self.assertIn("col_bool must have length", str(e.exception))

        with self.assertRaises(AssertionError) as e:
            sg.get_cols_to_keep(self.in_gct, cidx=[True, False, True])
        self.assertIn("cidx must be a list of integers", str(e.exception))

        with self.assertRaises(AssertionError) as e:
            sg.get_cols_to_keep(self.in_gct, cidx=[10])
        self.assertIn("cidx contains an integer", str(e.exception))

if __name__ == '__main__':
    setup_logger.setup(verbose=True)
    unittest.main()

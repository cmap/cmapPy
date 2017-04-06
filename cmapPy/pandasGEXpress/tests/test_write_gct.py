import unittest
import logging
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_logger
import os
import numpy as np
import pandas as pd
from cmapPy.pandasGEXpress import GCToo as GCToo
from cmapPy.pandasGEXpress import parse_gct as pg
from cmapPy.pandasGEXpress import write_gct as wg

FUNCTIONAL_TESTS_PATH = "functional_tests"
logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestWriteGct(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create dfs to be used by tests
        cls.data_df = pd.DataFrame(
            [[1, 2, 3], [5, 7, np.nan], [13, 17, -19], [0, 23, 29]],
            index=pd.Index(["rid1", "rid2", "rid3", "rid4"], name="rid"),
            columns=pd.Index(["cid1", "cid2", "cid3"], name="cid"), dtype=np.float32)
        cls.row_metadata_df = pd.DataFrame(
            [["Analyte 11", 11, "dp52"],
             ["Analyte 12", 12, "dp52"],
             ["Analyte 13", 13, "dp53"],
             ["Analyte 14", 14, "dp54"]],
            index=pd.Index(["rid1", "rid2", "rid3", "rid4"], name="rid"),
            columns=pd.Index(["pr_analyte_id", "pr_analyte_num", "pr_bset_id"], name="rhd"))
        cls.col_metadata_df = pd.DataFrame(
            [[8.38, np.nan, "DMSO", "24 h"],
             [7.7, np.nan, "DMSO", "24 h"],
             [8.18, np.nan, "DMSO", "24 h"]],
            index=pd.Index(["cid1", "cid2", "cid3"], name="cid"),
            columns=pd.Index(["qc_iqr", "pert_idose", "pert_iname", "pert_itime"], name="chd"))

    def test_main(self):
        out_name = os.path.join(FUNCTIONAL_TESTS_PATH, "test_main_out.gct")

        gctoo = GCToo.GCToo(data_df=self.data_df,
                            row_metadata_df=self.row_metadata_df,
                            col_metadata_df=self.col_metadata_df)
        wg.write(gctoo, out_name, data_null="NaN",
                 metadata_null="-666", filler_null="-666")

        # Read in the gct and verify that it's the same as gctoo
        new_gct = pg.parse(out_name)

        pd.util.testing.assert_frame_equal(new_gct.data_df, gctoo.data_df)
        pd.util.testing.assert_frame_equal(new_gct.row_metadata_df, gctoo.row_metadata_df)
        pd.util.testing.assert_frame_equal(new_gct.col_metadata_df, gctoo.col_metadata_df)

        # Also check that missing values were written to the file as expected
        in_df = pd.read_csv(out_name, sep="\t", skiprows=2, keep_default_na=False)
        self.assertEqual(in_df.iloc[0, 1], "-666")
        self.assertEqual(in_df.iloc[5, 6], "NaN")

        # Cleanup
        os.remove(out_name)

    def test_write_version_and_dims(self):
        # Write
        fname = "test_file.gct"
        f = open(fname, "wb")
        wg.write_version_and_dims("1.3", ["1", "2", "3", "4"], f)
        f.close()

        # Read and then remove
        f = open(fname, "r")
        version_string = f.readline().strip()
        dims = f.readline().strip().split("\t")
        f.close()
        os.remove(fname)

        # Check that it was written correctly
        self.assertEqual(version_string, "#1.3")
        self.assertEqual(dims, ["1", "2", "3", "4"])

    def test_write_top_half(self):
        # Write
        fname = "test_write_top_half.tsv"
        f = open(fname, "wb")
        wg.write_top_half(f, self.row_metadata_df, self.col_metadata_df, "-666", "-666")
        f.close()

        # Compare what was written to what was expected
        e_top_half = pd.DataFrame(
            [["id", "pr_analyte_id", "pr_analyte_num", "pr_bset_id", "cid1", "cid2", "cid3"],
             ["qc_iqr", "-666", "-666", "-666", "8.38", "7.7", "8.18"],
             ["pert_idose", "-666", "-666", "-666", "-666", "-666", "-666"],
             ["pert_iname", "-666", "-666", "-666", "DMSO", "DMSO", "DMSO"],
             ["pert_itime", "-666", "-666", "-666", "24 h", "24 h", "24 h"]])
        top_half = pd.read_csv(fname, sep="\t", header=None)
        pd.util.testing.assert_frame_equal(top_half, e_top_half)
        os.remove(fname)

    def test_write_bottom_half(self):
        # Write
        fname = "test_write_bottom_half.tsv"
        f = open(fname, "wb")
        wg.write_bottom_half(f, self.row_metadata_df, self.data_df, "NaN", "%.f", "-666")
        f.close()

        # Compare what was written to what was expected
        e_bottom_half = pd.DataFrame(
            [["rid1", "Analyte 11", 11, "dp52", 1., 2., 3.],
             ["rid2", "Analyte 12", 12, "dp52", 5., 7., np.nan],
             ["rid3", "Analyte 13", 13, "dp53", 13., 17., -19.],
             ["rid4", "Analyte 14", 14, "dp54", 0., 23., 29.]])
        bottom_half = pd.read_csv(fname, sep="\t", header=None)
        pd.util.testing.assert_frame_equal(bottom_half, e_bottom_half)
        os.remove(fname)

    def test_append_dims_and_file_extension(self):
        data_df = pd.DataFrame([[1, 2], [3, 4]])
        fname_no_gct = "a/b/file"
        fname_gct = "a/b/file.gct"
        e_fname = "a/b/file_n2x2.gct"

        fname_out = wg.append_dims_and_file_extension(fname_no_gct, data_df)
        self.assertEqual(fname_out, e_fname)

        fname_out = wg.append_dims_and_file_extension(fname_gct, data_df)
        self.assertEqual(fname_out, e_fname)

    def test_l1000_functional(self):
        l1000_in_path = os.path.join(FUNCTIONAL_TESTS_PATH, "test_l1000.gct")
        l1000_out_path = os.path.join(FUNCTIONAL_TESTS_PATH, "test_l1000_writing.gct")

        # Read in original gct file
        l1000_in_gct = pg.parse(l1000_in_path)

        # Read in new gct file
        wg.write(l1000_in_gct, l1000_out_path)
        l1000_out_gct = pg.parse(l1000_out_path)

        self.assertTrue(l1000_in_gct.data_df.equals(l1000_out_gct.data_df))
        self.assertTrue(l1000_in_gct.row_metadata_df.equals(l1000_out_gct.row_metadata_df))
        self.assertTrue(l1000_in_gct.col_metadata_df.equals(l1000_out_gct.col_metadata_df))

        # Clean up
        os.remove(l1000_out_path)

    def test_p100_functional(self):
        p100_in_path = os.path.join(FUNCTIONAL_TESTS_PATH, "test_p100.gct")
        p100_out_path = os.path.join(FUNCTIONAL_TESTS_PATH, "test_p100_writing.gct")

        # Read in original gct file
        p100_in_gct = pg.parse(p100_in_path)

        # Read in new gct file
        wg.write(p100_in_gct, p100_out_path)
        p100_out_gct = pg.parse(p100_out_path)

        self.assertTrue(p100_in_gct.data_df.equals(p100_out_gct.data_df))
        self.assertTrue(p100_in_gct.row_metadata_df.equals(p100_out_gct.row_metadata_df))
        self.assertTrue(p100_in_gct.col_metadata_df.equals(p100_out_gct.col_metadata_df))

        # Clean up
        os.remove(p100_out_path)

if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    unittest.main()

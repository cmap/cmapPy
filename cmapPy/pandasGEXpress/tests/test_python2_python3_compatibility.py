import logging
import unittest
import os
import numpy as np
import pandas as pd

import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.GCToo as GCToo
import cmapPy.pandasGEXpress.parse_gct as parse_gct
import cmapPy.pandasGEXpress.parse_gctx as parse_gctx
import cmapPy.pandasGEXpress.write_gct as write_gct
import cmapPy.pandasGEXpress.write_gctx as write_gctx


__author__ = "Saksham Malhotra"
__email__ = "saksham2196@gmail.com"

FUNCTIONAL_TESTS_PATH = "cmapPy/pandasGEXpress/tests/functional_tests/"
logger = logging.getLogger(setup_logger.LOGGER_NAME)


class TestPython2Python3Compatibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create GCtoo object with same high precision values.
        # These will remain same when implemented with python2 and python3.
        # Therefore, they can be used for testing writing and parsing of values.
        cls.data_df = pd.DataFrame(
            [[1.23131821, 92938193, 0.00101221], [22, 1.01201020, np.nan],
             [13231321, 17, -19.12033310], [0.00000121, 2312, 29]],
            index=pd.Index(["rid1", "rid2", "rid3", "rid4"], name="rid"),
            columns=pd.Index(["cid1", "cid2", "cid3"], name="cid"), dtype=np.float32)
        cls.row_metadata_df = pd.DataFrame(
            [["Analyte 11", 11, "dp52"],
             ["Analyte 12", 12, "dp52"],
             ["Analyte 13", 13, "dp53"],
             ["Analyte 14", 122314, "dp54"]],
            index=pd.Index(["rid1", "rid2", "rid3", "rid4"], name="rid"),
            columns=pd.Index(["pr_analyte_id", "pr_analyte_num", "pr_bset_id"], name="rhd"))
        cls.col_metadata_df = pd.DataFrame(
            [[np.nan, "DMSO", "24 h", 8.32121888],
             [np.nan, "DMSO", "24 h", 7.7121111],
             [np.nan, "DMSO", "24 h", 21228.18121290]],
            index=pd.Index(["cid1", "cid2", "cid3"], name="cid"),
            columns=pd.Index(["pert_idose", "pert_iname", "pert_itime", "qc_iqr"], name="chd"))

    def test_write_gct(self):
        out_name = os.path.join(FUNCTIONAL_TESTS_PATH, 'test_write_out_py2py3.gct')

        gctoo = GCToo.GCToo(data_df=self.data_df,
                            row_metadata_df=self.row_metadata_df,
                            col_metadata_df=self.col_metadata_df)
        write_gct.write(gctoo, out_name, data_null="NaN",
                        metadata_null="-666", filler_null="-666", data_float_format="%.8f")

        # Read in the gct and verify that it's the same as gctoo
        new_gct = parse_gct.parse(out_name)

        pd.testing.assert_frame_equal(new_gct.data_df, gctoo.data_df)
        pd.testing.assert_frame_equal(new_gct.row_metadata_df, gctoo.row_metadata_df)
        pd.testing.assert_frame_equal(new_gct.col_metadata_df, gctoo.col_metadata_df)

        # Also check that missing values were written to the file as expected
        in_df = pd.read_csv(out_name, sep="\t", skiprows=2, keep_default_na=False)
        self.assertEqual(in_df.iloc[0, 1], "-666")
        self.assertEqual(in_df.iloc[5, 6], "NaN")

        # Cleanup
        os.remove(out_name)

    def test_parse_gct(self):
        # tests the parsing of a gct file with high precision values
        gct_filepath = os.path.join(FUNCTIONAL_TESTS_PATH, 'test_l1000_highprecision.gct')
        data_gct = parse_gct.parse(gct_filepath)

        (data, row_metadata, col_metadata) = (data_gct.data_df, data_gct.row_metadata_df, data_gct.col_metadata_df)
        e_dims = [978, 377, 11, 35]
        actual_version = 'GCT1.3'

        # Check shapes of outputs
        self.assertTrue(row_metadata.shape == (e_dims[0], e_dims[2]),
                        ("row_metadata.shape = {} " +
                         "but expected it to be ({}, {})").format(row_metadata.shape,
                                                                  e_dims[0], e_dims[2]))
        self.assertTrue(col_metadata.shape == (e_dims[1], e_dims[3]),
                        ("col_metadata.shape = {} " +
                         "but expected it to be ({}, {})").format(col_metadata.shape,
                                                                  e_dims[1], e_dims[3]))
        self.assertTrue(data.shape == (e_dims[0], e_dims[1]),
                        ("data.shape = {} " +
                         "but expected it to be ({}, {})").format(data.shape,
                                                                  e_dims[0], e_dims[1]))
        # Check version
        self.assertEqual(actual_version, data_gct.version)

        # Check the type of data
        self.assertTrue(isinstance(data.iloc[0, 0], np.float32),
                        "The data should be a float32, not {}".format(type(data.iloc[0, 0])))

        # Check a few high precision floating values in data
        correct_val = np.float32(11.574655)
        self.assertTrue(data.iloc[0, 0] == correct_val,
                        ("The first value in the data matrix should be " +
                         "{} not {}").format(correct_val, data.iloc[0, 0]))
        correct_val = np.float32(5.3183546)
        self.assertTrue(data.iloc[e_dims[0] - 1, e_dims[1] - 1] == correct_val,
                        ("The last value in the data matrix should be " +
                         str(correct_val) + " not {}").format(data.iloc[e_dims[0] - 1, e_dims[1] - 1]))

    def test_write_gctx(self):
        out_name = os.path.join(FUNCTIONAL_TESTS_PATH, 'test_write_out_py2py3.gctx')

        gctoo = GCToo.GCToo(data_df=self.data_df,
                            row_metadata_df=self.row_metadata_df,
                            col_metadata_df=self.col_metadata_df)
        write_gctx.write(gctoo, out_name,
                         convert_back_to_neg_666=True, gzip_compression_level=6,
                         max_chunk_kb=1024, matrix_dtype=np.float32)

        # Read in the gct and verify that it's the same as gctoo
        # re-ininitalising gctooo because write_gctx is changing dtype of one column of col_metadata_df
        gctoo = GCToo.GCToo(data_df=self.data_df,
                            row_metadata_df=self.row_metadata_df,
                            col_metadata_df=self.col_metadata_df)

        new_gctx = parse_gctx.parse(out_name)

        pd.testing.assert_frame_equal(new_gctx.data_df, gctoo.data_df)
        pd.testing.assert_frame_equal(new_gctx.row_metadata_df, gctoo.row_metadata_df)
        pd.testing.assert_frame_equal(new_gctx.col_metadata_df, gctoo.col_metadata_df)

        # Cleanup
        os.remove(out_name)

    def test_parse_gctx(self):
        # tests the parsing of a gct file with high precision values
        gctx_filepath = os.path.join(FUNCTIONAL_TESTS_PATH, 'test_l1000_highprecision.gctx')
        data_gctx = parse_gctx.parse(gctx_filepath)

        (data, row_metadata, col_metadata) = (data_gctx.data_df, data_gctx.row_metadata_df, data_gctx.col_metadata_df)
        e_dims = [978, 377, 11, 37]
        actual_version = 'GCTX1.0'

        # Check shapes of outputs
        self.assertTrue(row_metadata.shape == (e_dims[0], e_dims[2]),
                        ("row_metadata.shape = {} " +
                         "but expected it to be ({}, {})").format(row_metadata.shape,
                                                                  e_dims[0], e_dims[2]))
        self.assertTrue(col_metadata.shape == (e_dims[1], e_dims[3]),
                        ("col_metadata.shape = {} " +
                         "but expected it to be ({}, {})").format(col_metadata.shape,
                                                                  e_dims[1], e_dims[3]))
        self.assertTrue(data.shape == (e_dims[0], e_dims[1]),
                        ("data.shape = {} " +
                         "but expected it to be ({}, {})").format(data.shape,
                                                                  e_dims[0], e_dims[1]))
        # Check version
        self.assertEqual(actual_version, data_gctx.version.decode())

        # Check the type of data
        self.assertTrue(isinstance(data.iloc[0, 0], np.float32),
                        "The data should be a float32, not {}".format(type(data.iloc[0, 0])))

        # Check a few high precision floating values in data
        correct_val = np.float32(0.3473286032676697)
        self.assertTrue(data.iloc[0, 0] == correct_val,
                        ("The first value in the data matrix should be " +
                         "{} not {}").format(correct_val, data.iloc[0, 0]))
        correct_val = np.float32(-0.624971330165863)
        self.assertTrue(data.iloc[e_dims[0] - 1, e_dims[1] - 1] == correct_val,
                        ("The last value in the data matrix should be " +
                         str(correct_val) + " not {}").format(data.iloc[e_dims[0] - 1, e_dims[1] - 1]))


if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    unittest.main()

import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import unittest
import pandas.util.testing as pandas_testing
import cmapPy.pandasGEXpress.subset_gctoo as subset_gctoo
import cmapPy.pandasGEXpress.mini_gctoo_for_testing as mini_gctoo_for_testing
import cmapPy.pandasGEXpress.parse as parse

__author__ = "Oana Enache"
__email__ = "oana@broadinstitute.org"

FUNCTIONAL_TESTS_PATH = "functional_tests"

logger = logging.getLogger(setup_logger.LOGGER_NAME)

class TestParse(unittest.TestCase):
    def test_gctx_parsing(self):
        # parse in gctx, no other arguments        
        mg1 = mini_gctoo_for_testing.make()
        mg2 = parse.parse("functional_tests/mini_gctoo_for_testing.gctx")

        pandas_testing.assert_frame_equal(mg1.data_df, mg2.data_df)
        pandas_testing.assert_frame_equal(mg1.row_metadata_df, mg2.row_metadata_df)
        pandas_testing.assert_frame_equal(mg1.col_metadata_df, mg2.col_metadata_df) 

        # check convert_neg_666 worked correctly
        self.assertTrue(mg2.col_metadata_df["mfc_plate_id"].isnull().all())

        # parse w/o convert_neg_666
        mg2_alt = parse.parse("functional_tests/mini_gctoo_for_testing.gctx", convert_neg_666 = False)
        self.assertFalse(mg2_alt.col_metadata_df["mfc_plate_id"].isnull().all())        

        # parsing w/rids & cids specified 
        test_rids = ['LJP007_MCF10A_24H:TRT_CP:BRD-K93918653:3.33', 'LJP007_MCF7_24H:CTL_VEHICLE:DMSO:-666']
        test_cids = ['LJP007_MCF7_24H:TRT_POSCON:BRD-A61304759:10']
        mg3 = subset_gctoo.subset_gctoo(mg1, rid=test_rids, cid=test_cids)
        mg4 = parse.parse("functional_tests/mini_gctoo_for_testing.gctx",
                    rid=test_rids, cid=test_cids)
        pandas_testing.assert_frame_equal(mg3.data_df, mg4.data_df)
        pandas_testing.assert_frame_equal(mg3.row_metadata_df, mg4.row_metadata_df)
        pandas_testing.assert_frame_equal(mg3.col_metadata_df, mg4.col_metadata_df)

        # parsing w/ridx & cidx specified 
        mg5 = subset_gctoo.subset_gctoo(mg1, rid=['LJP007_MCF7_24H:CTL_VEHICLE:DMSO:-666'],
                                      cid=['LJP007_MCF7_24H:CTL_VEHICLE:DMSO:-666'])
        mg6 = parse.parse("functional_tests/mini_gctoo_for_testing.gctx", ridx=[4], cidx=[4])

        pandas_testing.assert_frame_equal(mg5.data_df, mg6.data_df)
        pandas_testing.assert_frame_equal(mg5.row_metadata_df, mg6.row_metadata_df)
        pandas_testing.assert_frame_equal(mg5.col_metadata_df, mg6.col_metadata_df)

        # parsing row metadata only
        mg7 = parse.parse("functional_tests/mini_gctoo_for_testing.gctx", row_meta_only=True)
        pandas_testing.assert_frame_equal(mg7, mg1.row_metadata_df)

        # parsing col metadata only
        mg8 = parse.parse("functional_tests/mini_gctoo_for_testing.gctx", col_meta_only=True)
        pandas_testing.assert_frame_equal(mg8, mg1.col_metadata_df)

        # parsing w/multiindex
        mg9 = parse.parse("functional_tests/mini_gctoo_for_testing.gctx", make_multiindex=True)
        self.assertTrue(mg9.multi_index_df is not None)

    def test_gct_parsing(self):
        # parse in gct, no other arguments
        mg1 = mini_gctoo_for_testing.make()
        mg2 = parse.parse("functional_tests/mini_gctoo_for_testing.gct")

        pandas_testing.assert_frame_equal(mg1.data_df, mg2.data_df)
        pandas_testing.assert_frame_equal(mg1.row_metadata_df, mg2.row_metadata_df)
        pandas_testing.assert_frame_equal(mg1.col_metadata_df, mg2.col_metadata_df)

        # check convert_neg_666 worked correctly
        self.assertTrue(mg2.col_metadata_df["mfc_plate_id"].isnull().all())

        # parse w/o convert_neg_666
        mg2_alt = parse.parse("functional_tests/mini_gctoo_for_testing.gct", convert_neg_666 = False)
        self.assertItemsEqual(mg2_alt.col_metadata_df["mfc_plate_id"].values.tolist(),
                              [-666] * 6)

        # parse in gct with subsetting
        my_rid = "LJP007_MCF10A_24H:TRT_CP:BRD-K93918653:3.33"
        mg3 = parse.parse("functional_tests/mini_gctoo_for_testing.gct",
                          cidx=[0, 2], rid=[my_rid])

        self.assertEqual(mg3.data_df.shape, (1, 2))
        self.assertItemsEqual(mg3.data_df.values.flatten().tolist(), [1., 3.])
        self.assertEqual(mg3.row_metadata_df.index[0], my_rid)

if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    unittest.main()




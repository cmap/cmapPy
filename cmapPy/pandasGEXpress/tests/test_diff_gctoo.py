import unittest
import logging
import pandas as pd
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.GCToo as GCToo
import cmapPy.pandasGEXpress.diff_gctoo as diff_gctoo

logger = logging.getLogger(setup_logger.LOGGER_NAME)

test_mat = pd.DataFrame({'A':[4,2,3], 'B': [2,8,6], 'C': [6,5,9],
                         'D': [5,2,1], 'E':[8,8,6], 'F': [7,6,6]})
test_col_meta = pd.DataFrame(
    {'pert_type': ['trt_cp', 'trt_cp', 'trt_cp',
                   'trt_cp', 'ctl_vehicle', 'ctl_vehicle'],
     'pert_iname': ['bort', 'bort', 'DMSO', 'DMSO', 'bort', 'bort']},
    index=['A', 'B', 'C', 'D', 'E', 'F'])
test_gctoo = GCToo.GCToo(data_df=test_mat,
                         col_metadata_df=test_col_meta)


class TestDifferential(unittest.TestCase):
    def test_diff_gctoo_pc(self):
        pc_zscores = diff_gctoo.diff_gctoo(test_gctoo, plate_control=True, lower_diff_thresh=-2)
        self.assertTrue(pc_zscores.data_df.shape == (3, 6))

        pd.util.testing.assert_frame_equal(pc_zscores.data_df, pd.DataFrame(
            {'A': [-0.6745, -0.9443, -1.349],
             'C': [0.2248, -0.1349, 1.349],
             'B': [-1.5738, 0.6745, 0.0], 'E': [1.1242, 0.6745, 0.0],
             'D': [-0.2248, -0.9443, -2], # last val should be -2 bc of thresholding
             'F': [0.6745, 0.1349, 0.0]}))

        # test diff_method assertion
        with self.assertRaises(AssertionError) as e:
            diff_gctoo.diff_gctoo(test_gctoo, plate_control=True, diff_method="robust_zs")
        self.assertIn("diff_method: robust_zs", str(e.exception))

        # test median norm
        pc_median_normed_df = diff_gctoo.diff_gctoo(test_gctoo, diff_method="median_norm")
        self.assertEqual(pc_median_normed_df.data_df.iloc[0, 0], -1.5)
        self.assertEqual(pc_median_normed_df.data_df.loc[2, "B"], 0)

    def test_diff_gctoo_vc(self):
        vc_zscores1 = diff_gctoo.diff_gctoo(test_gctoo, plate_control=False)
        vc_zscores2 = diff_gctoo.diff_gctoo(test_gctoo, plate_control=False,
                                            group_field='pert_iname',
                                            group_val='DMSO')
        self.assertTrue(vc_zscores1.data_df.shape == (3, 6))
        self.assertTrue(vc_zscores2.data_df.shape == (3, 6))

        pd.util.testing.assert_frame_equal(vc_zscores1.data_df, pd.DataFrame(
            {'A': [-4.7214, -3.3725, -10.0], # check for thresholding
             'C': [-2.0235, -1.349, 10.0],
             'B': [-7.4194, 0.6745, 0.0],
             'E': [0.6745, 0.6745, 0.0],
             'D': [-3.3725, -3.3725, -10.0],
             'F': [-0.6745, -0.6745, 0.0]}))

        pd.util.testing.assert_frame_equal(vc_zscores2.data_df, pd.DataFrame(
            {'A': [-2.0235, -0.6745, -0.3372],
             'C': [0.6745, 0.6745, 0.6745],
             'B': [-4.7214, 2.0235, 0.1686],
             'E': [3.3725, 2.0235, 0.1686],
             'D': [-0.6745, -0.6745, -0.6745],
             'F': [2.0235, 1.1242, 0.1686]}))

        # test group_val assertion
        with self.assertRaises(AssertionError) as e:
            diff_gctoo.diff_gctoo(test_gctoo, plate_control=False, group_val="dmso")
        self.assertIn("dmso not present", str(e.exception))


if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    unittest.main()


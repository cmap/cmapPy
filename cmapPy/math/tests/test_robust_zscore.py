import unittest
import logging
import pandas as pd
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.math.robust_zscore as robust_zscore

logger = logging.getLogger(setup_logger.LOGGER_NAME)

test_mat = pd.DataFrame({'A':[4,2,3], 'B': [2,8,6], 'C': [6,5,9], 'D': [5,2,1]})
test_ctl_mat = pd.DataFrame({'E':[8,8,6], 'F': [7,6,6]})
test_ctl_mat2 = pd.DataFrame({'E':[8,8,6], 'F': [8,6,6]})


class TestRobustZscore(unittest.TestCase):
    def test_zscore_pc(self):
        pc_zscores = robust_zscore.robust_zscore(test_mat)
        self.assertTrue(pc_zscores.shape == (3, 4))

        pd.util.testing.assert_frame_equal(pc_zscores, pd.DataFrame(
            {'A': [-0.3372, -0.6745, -0.4047],
             'B': [-1.6862, 2.0235, 0.4047],
             'C': [1.0117, 0.6745, 1.2141],
             'D': [0.3372, -0.6745, -0.9443]}))

    def test_zscore_vc(self):
        vc_zscores = robust_zscore.robust_zscore(test_mat, ctrl_mat=test_ctl_mat)
        self.assertTrue(vc_zscores.shape == (3, 4))
        pd.util.testing.assert_frame_equal(vc_zscores, pd.DataFrame(
            {'A': [-4.7214, -3.3725, -20.2347],
             'B': [-7.4194, 0.6745, 0.0],
             'C': [-2.0235, -1.349, 20.2347],
             'D': [-3.3725, -3.3725, -33.7245]}))

        # check that min_mad works
        vc_zscores2 = robust_zscore.robust_zscore(test_mat, ctrl_mat=test_ctl_mat2)
        self.assertEqual(vc_zscores2.iloc[0, 0], -26.9796)
        self.assertEqual(vc_zscores2.iloc[1, 1], 0.6745)

if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    unittest.main()

import unittest
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import logging
import pandas as pd
import sys
import cmapPy.math.robust_zscore as robust_zscore

logger = logging.getLogger(setup_logger.LOGGER_NAME)

test_mat = pd.DataFrame({'A':[4,2,3], 'B': [2,8,6], 'C': [6,5,9], 'D': [5,2,1]})
test_ctl_mat = pd.DataFrame({'E':[8,8,6], 'F': [7,6,6]})

class TestRobustZscore(unittest.TestCase):
    def test_zscore_pc(self):
        pc_zscores = robust_zscore.calc_zscore(test_mat)
        self.assertTrue(pc_zscores.shape == (3,4))
        self.assertTrue(pc_zscores.loc[0].tolist() == [-0.3372, -1.6862, 1.0117, 0.3372])
        self.assertTrue(pc_zscores.loc[1].tolist() == [-0.6745, 2.0235, 0.6745, -0.6745])
        self.assertTrue(pc_zscores.loc[2].tolist() == [-0.4047, 0.4047, 1.2141, -0.9443])

    def test_zscore_vc(self):
        vc_zscores = robust_zscore.calc_zscore(test_mat, ctrl_mat = test_ctl_mat)
        self.assertTrue(vc_zscores.shape == (3, 4))
        self.assertTrue(vc_zscores.loc[0].tolist() == [-4.7214, -7.4194, -2.0235, -3.3725])
        self.assertTrue(vc_zscores.loc[1].tolist() == [-3.3725, 0.6745, -1.349, -3.3725])
        self.assertTrue(vc_zscores.loc[2].tolist() == [-20.2347, 0.0, 20.2347, -33.7245])

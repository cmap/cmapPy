import unittest
import logging
import pandas as pd
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.math.agg_wt_avg as agg_wt_avg

logger = logging.getLogger(setup_logger.LOGGER_NAME)

test_mat = pd.DataFrame({'A':[1,2,3], 'B': [2,8,6], 'C': [6,8,9]})
test_mat_corr = test_mat.corr()


class TestAggWtAvg(unittest.TestCase):
    def test_calculate_weights(self):
        # happy path
        raw_weights, weights = agg_wt_avg.calculate_weights(test_mat_corr, min_wt=0.1)
        self.assertTrue(len(weights == 3))
        self.assertTrue(raw_weights.tolist() == [0.8183, 0.7202, 0.8838])
        self.assertTrue(weights.tolist() == [0.3378, 0.2973, 0.3649])

        # test that min_wt works
        raw_weights2, weights2 = agg_wt_avg.calculate_weights(test_mat_corr, min_wt=0.85)
        self.assertEqual(raw_weights2[1], 0.85)

    def test_get_upper_triangle(self):
        # happy path
        upper_tri_df = agg_wt_avg.get_upper_triangle(test_mat_corr)
        self.assertTrue(upper_tri_df['corr'].tolist() == [0.6547, 0.982, 0.7857])
        self.assertTrue(upper_tri_df['rid'].tolist() == ['B', 'C', 'C'])
        self.assertTrue(upper_tri_df['index'].tolist() == ['A', 'A', 'B'])

    def test_agg_wt_avg(self):
        # use spearman
        out_sig, upper_tri_df, raw_weights, weights = agg_wt_avg.agg_wt_avg(test_mat)
        self.assertTrue(out_sig.tolist() == [3.125, 5.75, 6.0])
        self.assertAlmostEqual(upper_tri_df.loc[upper_tri_df.index[0], "corr"], 0.5)
        self.assertAlmostEqual(raw_weights[0], 0.75)
        self.assertAlmostEqual(weights[0], 0.375)

        # test on a single signature
        out_sig2, _, _, _ = agg_wt_avg.agg_wt_avg(test_mat[["C"]])
        pd.util.testing.assert_frame_equal(out_sig2, test_mat[["C"]])

        # should break if empty input
        with self.assertRaises(AssertionError) as e:
            agg_wt_avg.agg_wt_avg(test_mat[[]])
        self.assertIn("mat is empty!", str(e.exception))

if __name__ == "__main__":
    setup_logger.setup(verbose=True)
    unittest.main()


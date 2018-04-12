import unittest
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import logging
import pandas as pd
import sys
import cmapPy.math.modz as modz


logger = logging.getLogger(setup_logger.LOGGER_NAME)

test_mat = pd.DataFrame({'A':[1,2,3], 'B': [2,8,6], 'C': [6,8,9]})

class TestModz(unittest.TestCase):
    def test_calculate_weights(self):
        raw_weights, weights = modz.calculate_weights(test_mat.corr())
        self.assertTrue(len(weights == 3))
        self.assertTrue(raw_weights.tolist() == [0.8183, 0.7202, 0.8838])
        self.assertTrue(weights.tolist() == [0.3378, 0.2973, 0.3649])

    def test_upper_triangle(self):
        upper_tri_series = modz.upper_triangle(test_mat.corr())
        self.assertTrue(upper_tri_series['corr'].tolist() == [0.6547, 0.982, 0.7857])
        self.assertTrue(upper_tri_series['rid'].tolist() == ['B', 'C', 'C'])
        self.assertTrue(upper_tri_series['index'].tolist() == ['A', 'A', 'B'])

    def test_main(self):
        modz_values, x, y, z = modz.calc_modz(test_mat)
        self.assertTrue(modz_values.tolist() == [3.125, 5.75, 6.0])




'''
Created on Sep 30, 2019

@author: Navid Dianati
@contact: navid@broadinstitute.org
'''
import unittest
import stratogram
import pandas as pd
import matplotlib.pyplot as plt


class Test(unittest.TestCase):

    def testStratogram(self):
        filename = "./test_files/PBRANT_CYCLE1_key_metrics_expanded_sample.txt"
        df = pd.read_csv(filename, sep="\t")
        metrics = ['ss_ltn2', 'cc_q75', 'spec_vi', 'mag_vi']
        column_names = ['Strength', 'Reproducibility', 'specificity', 'magnitude']
        stratogram.stratogram(
            df,
            category="category_label_abridged",
            category_order="category_order",
            metrics=metrics,
            column_display_names=column_names,
            )
        plt.show()

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testStratogram']
    unittest.main()

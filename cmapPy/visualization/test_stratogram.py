'''
Created on Sep 30, 2019

@author: Navid Dianati
@contact: navid@broadinstitute.org
'''
import unittest

import matplotlib.pyplot as plt
import pandas as pd
import stratogram


class Test(unittest.TestCase):

    def testStratogram(self):
        filename = "./test_files/PBRANT_CYCLE1_key_metrics_expanded_sample.txt"
        df = pd.read_csv(filename, sep="\t")
        metrics = ['ss_ltn2', 'cc_q75', 'spec_vi', 'mag_vi']
        column_names = ['Strength', 'Reproducibility', 'specificity', 'magnitude']
        stratogram.stratogram(
            df,
            category_definition="category_label",
            category_label="category_label_abridged",
            category_order="category_order",
            metrics=metrics,
            figsize=(20, 15),
            column_display_names=column_names,
            xtick_orientation="horizontal",
            ylabel_fontsize=15,
            xlabel_fontsize=15,
            xlabel_fontcolor="#555555",
            ylabel_fontcolor="#555555",
            fontfamily="Roboto"
            )
        plt.savefig("./test_files/stratogram_test.png", dpi=150)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testStratogram']
    unittest.main()

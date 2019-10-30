'''
Created on Sep 30, 2019

@author: Navid Dianati
@contact: navid@broadinstitute.org
'''
import unittest

import matplotlib.pyplot as plt
import pandas as pd
import scattergram


class Test(unittest.TestCase):

    def testScattergram1(self):
        filename = "./test_files/PBRANT_CYCLE1_key_metrics_expanded_sample.txt"
        df = pd.read_csv(filename, sep="\t")
        plot_columns = ['ss_ltn2', 'cc_q75', 'spec_vi', 'mag_vi']
        column_names = ['Strength', 'Reproducibility', 'specificity', 'magnitude']
        scattergram.scattergram(
            df,
            columns=plot_columns,
            column_names=column_names,
            title="This is a test"
            )
        plt.show()
    
    def testScattergram2(self):
        filename = "./test_files/PBRANT_CYCLE1_key_metrics_expanded_sample.txt"
        df = pd.read_csv(filename, sep="\t")
        plot_columns = ['ss_ltn2', 'cc_q75', 'spec_vi', 'mag_vi']
        column_names = ['Strength', 'Reproducibility', 'specificity', 'magnitude']
        scattergram.scattergram(
            df,
            columns=plot_columns,
            column_names=column_names,
            title="This is a test",
            outfile="./test_files/deleteme.png",
            fig_dpi=50
            )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testScattergram']
    unittest.main()

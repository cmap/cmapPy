'''
Created on Sep 30, 2019

@author: Navid Dianati
@contact: navid@broadinstitute.org
'''
import unittest
import scattergram
import pandas as pd
import matplotlib.pyplot as plt


class Test(unittest.TestCase):


    def testScattergram(self):
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
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testScattergram']
    unittest.main()
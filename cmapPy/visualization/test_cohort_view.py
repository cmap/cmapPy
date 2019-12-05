'''
Created on Sep 30, 2019

@author: Navid Dianati
@contact: navid@broadinstitute.org
'''
import unittest

import cohort_view
import matplotlib.pyplot as plt
import pandas as pd


class Test(unittest.TestCase):

    def testCohortView(self):
        filename = "./test_files/PBRANT_CYCLE1_key_metrics_expanded_sample.txt"
        df = pd.read_csv(filename, sep="\t")

        df['is_reproducible'] = (df['cc_q75'] > 0.2) + 0
        df['is_high_mag'] = (df['mag_vi'] > 0.2) + 0
        flags = ['is_reproducible', 'is_high_mag']
        column_names = ['Reproducible', 'magnitude']
        table = cohort_view.cohort_view_table(
            df,
            category_label="category_label",
            category_order="category_order",
            flags=flags,
            flag_display_labels=column_names
            
            )
        print(table)
#         plt.savefig("./test_files/cohort_view_test.html", dpi=150)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testStratogram']
    unittest.main()

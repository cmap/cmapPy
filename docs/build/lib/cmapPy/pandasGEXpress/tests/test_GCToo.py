import unittest
import pandas as pd
import numpy as np
import logging
from cmapPy.pandasGEXpress import setup_GCToo_logger as setup_GCToo_logger
from cmapPy.pandasGEXpress import GCToo as GCToo 
from random import shuffle

logger = logging.getLogger(setup_GCToo_logger.LOGGER_NAME)

class TestGctoo(unittest.TestCase):

    def test_init(self):
        # Create test data
        data_df = pd.DataFrame([[1, 2, 3], [4, 5, 6]],
                               index=["A", "B"], columns=["a", "b", "c"])
        row_metadata_df = pd.DataFrame([["rhd_A", "rhd_B"], ["rhd_C", "rhd_D"]],
                                       index=["A", "B"], columns=["rhd1", "rhd2"])
        col_metadata_df = pd.DataFrame(["chd_a", "chd_b", "chd_c"],
                                       index=["a", "b", "c"], columns=["chd1"])

        # happy path, no multi-index 
        my_gctoo1 = GCToo.GCToo(data_df=data_df, row_metadata_df=row_metadata_df,
                    col_metadata_df=col_metadata_df)

        self.assertTrue(my_gctoo1.multi_index_df == None, 
            'Expected no multi-index DataFrame but found {}'.format(my_gctoo1.multi_index_df))

        # happy path, with multi-index 
        my_gctoo2 = GCToo.GCToo(data_df=data_df, row_metadata_df=row_metadata_df,
                    col_metadata_df=col_metadata_df, make_multiindex = True)

        self.assertTrue(isinstance(my_gctoo2.multi_index_df.index, pd.core.index.MultiIndex), 
            "Expected a multi_index DataFrame but instead found {}". format(my_gctoo2.multi_index_df))

    def test__setattr__(self):
        # case 1: not init yet, should just run __init__ 
        # Create test data
        data_df = pd.DataFrame([[1, 2, 3], [4, 5, 6]],
                               index=["A", "B"], columns=["a", "b", "c"])
        row_metadata_df = pd.DataFrame([["rhd_A", "rhd_B"], ["rhd_C", "rhd_D"]],
                                       index=["A", "B"], columns=["rhd1", "rhd2"])
        col_metadata_df = pd.DataFrame(["chd_a", "chd_b", "chd_c"],
                                       index=["a", "b", "c"], columns=["chd1"])

        ## happy path, no multi-index 
        my_gctoo1 = GCToo.GCToo(data_df=data_df, row_metadata_df=row_metadata_df,
                    col_metadata_df=col_metadata_df)
                    
        ## reset row_metadata_df: happy case
        new_row_meta1 = my_gctoo1.row_metadata_df.copy()

        new_rid_order = ["B", "A"]
   
        new_row_meta1.index = new_rid_order
        # shouldn't have any problems re-setting row_meta 
        my_gctoo1.row_metadata_df = new_row_meta1

        ## reset row_metadata_df: to not a DF 
        new_row_meta2 = "this is my new row metadata"

        with self.assertRaises(Exception) as context:
            my_gctoo1.row_metadata_df = new_row_meta2 
        self.assertTrue("expected Pandas DataFrame, got something else" in str(context.exception))     

        ## reset row_metadata_df: non-matching index values 
        new_row_meta3 = my_gctoo1.row_metadata_df.copy()
        new_row_meta3.index = ["thing1", "thing2"]

        with self.assertRaises(Exception) as context:
            my_gctoo1.row_metadata_df = new_row_meta3
        self.assertTrue("The rids are inconsistent between data_df and row_metadata_df" in str(context.exception))

        ## reset row_metadata_df: not unique index values 
        new_row_meta4 = my_gctoo1.row_metadata_df.copy()
        new_row_meta4.index = ["A", "A"]

        with self.assertRaises(Exception) as context:
            my_gctoo1.row_metadata_df = new_row_meta4
        self.assertTrue("Index values must be unique" in str(context.exception))

        my_gctoo2 = GCToo.GCToo(data_df=data_df, row_metadata_df=row_metadata_df,
                    col_metadata_df=col_metadata_df)

        ## reset col_metadata_df: happy case
        new_col_meta1 = my_gctoo2.col_metadata_df.copy()

        new_cid_order = ["c", "a", "b"]
        new_col_meta1.index = new_cid_order

        # shouldn't have any problems
        my_gctoo2.col_metadata_df = new_col_meta1
        
        ## reset col_metadata_df: to not a DF 
        new_col_meta2 = "this is my new col metadata"

        with self.assertRaises(Exception) as context:
            my_gctoo2.col_metadata_df = new_col_meta2 
        self.assertTrue("expected Pandas DataFrame, got something else" in str(context.exception))     
       
        ## reset col_metadata_df: non-matching index values 
        new_col_meta3 = my_gctoo2.col_metadata_df.copy()
        new_col_meta3.index = ["thing1", "thing2", "thing3"]

        with self.assertRaises(Exception) as context:
            my_gctoo2.col_metadata_df = new_col_meta3
        self.assertTrue("The cids are inconsistent between data_df and col_metadata_df" in str(context.exception))

        ## reset col_metadata_df: not unique index values 
        new_col_meta4 = my_gctoo2.col_metadata_df.copy()
        new_col_meta4.index = ["a", "b", "a"]

        with self.assertRaises(Exception) as context:
            my_gctoo2.col_metadata_df = new_col_meta4
        self.assertTrue("Index values must be unique" in str(context.exception))

        my_gctoo3 = GCToo.GCToo(data_df=data_df, row_metadata_df=row_metadata_df,
                    col_metadata_df=col_metadata_df)

        ## reset data_df: happy case
        new_data_df1 = my_gctoo3.data_df.copy() 
        new_data_df1.index = ["B","A"]
        new_data_df1.columns = ["c", "b", "a"]

        # shouldn't have problems 
        my_gctoo3.data_df = new_data_df1

        ## reset data_df: row_meta doesn't match
        new_data_df2 = my_gctoo3.data_df.copy()
        new_data_df2.index = ["blah", "boop"]

        with self.assertRaises(Exception) as context:
            my_gctoo3.data_df = new_data_df2
        self.assertTrue("The rids are inconsistent between data_df and row_metadata_df" in str(context.exception))

        ## reset data_df: col_meta doesn't match 
        new_data_df3 = my_gctoo3.data_df.copy()
        new_data_df3.columns = ["x", "y", "z"]

        with self.assertRaises(Exception) as context:
            my_gctoo3.data_df = new_data_df3
        self.assertTrue("The cids are inconsistent between data_df and col_metadata_df" in str(context.exception))

        my_gctoo4 = GCToo.GCToo(data_df=data_df, row_metadata_df=row_metadata_df,
                    col_metadata_df=col_metadata_df, make_multiindex= True)

        ## try to reset multi-index (shouldn't work)
        new_multi_index = my_gctoo4.multi_index_df.copy()

        with self.assertRaises(Exception) as context:
            my_gctoo1.multi_index_df = new_multi_index
        self.assertTrue("Cannot reassign value of multi_index_df attribute;" in str(context.exception))

        ## reset src 
        my_gctoo1.src = "other_src"
        self.assertTrue(my_gctoo1.src == "other_src", 
            ("src should just be re-set with object's set_attr method but doesn't appear to be") +
            (" expected {} but found {}").format("other_src", my_gctoo1.src))

        ## reset version
        my_gctoo1.version = "other_version"
        self.assertTrue(my_gctoo1.version == "other_version", 
            ("version should just be re-set with object's set_attr method but doesn't appear to be") +
            ("expected {} but found {}").format("other_version", my_gctoo1.version))
      


    def test_check_df(self):
        not_unique_data_df = pd.DataFrame([[1, 2, 3], [4, 5, 6]],
                                          index=["A", "B"], columns=["a", "b", "a"])
        not_unique_rhd = pd.DataFrame([["rhd_A", "rhd_B"], ["rhd_C", "rhd_D"]],
                                       index=["A", "B"], columns=["rhd1", "rhd1"])
        """
        # case 3: row subsetting - sample subset > og # of samples
        with self.assertRaises(AssertionError) as context:
            random_slice.make_specified_size_gctoo(mini_gctoo, 30, "row")
        self.assertTrue("number of entries must be smaller than dimension being subsetted " in str(context.exception))

        """
        # cids in data_df are not unique
        with self.assertRaises(Exception) as context:
            GCToo.GCToo(data_df=not_unique_data_df, 
                row_metadata_df=pd.DataFrame(index=["A","B"]),
                col_metadata_df=pd.DataFrame(index=["a","b","c"]))
            print(str(not_unique_data_df.columns))
            self.assertTrue(str(not_unique_data_df.columns) in str(context.exception))

        # rhds are not unique in row_metadata_df
        with self.assertRaises(Exception) as context:
            GCToo.GCToo(data_df=pd.DataFrame([[1, 2, 3], [4, 5, 6]], index=["A","B"], columns=["a","b","c"]),
                row_metadata_df=not_unique_rhd,
                col_metadata_df=pd.DataFrame(index=["a","b","c"]))
            self.assertTrue("'rhd1' 'rhd1'" in str(context.exception))

    def test_assemble_multi_index_df(self):

        # TODO: Add test of only row ids present as metadata
        # TODO: Add test of only col ids present as metadata 

        g = GCToo.GCToo(data_df = pd.DataFrame({10:range(13,16), 11:range(16,19), 12:range(19,22)}, index=range(4,7)),
            row_metadata_df=pd.DataFrame({"a":range(3)}, index=range(4,7)),
            col_metadata_df=pd.DataFrame({"b":range(7,10)}, index=range(10,13)),
            make_multiindex = True)

        assert "a" in g.multi_index_df.index.names, g.multi_index_df.index.names
        assert "rid" in g.multi_index_df.index.names, g.multi_index_df.index.names

        assert "b" in g.multi_index_df.columns.names, g.multi_index_df.columns.names
        assert "cid" in g.multi_index_df.columns.names, g.multi_index_df.columns.names

        r = g.multi_index_df.xs(7, level="b", axis=1)
        logger.debug("r:  {}".format(r))
        assert r.xs(4, level="rid", axis=0).values[0][0] == 13, r.xs(4, level="rid", axis=0).values[0][0]
        assert r.xs(5, level="rid", axis=0).values[0][0] == 14, r.xs(5, level="rid", axis=0).values[0][0]
        assert r.xs(6, level="rid", axis=0).values[0][0] == 15, r.xs(6, level="rid", axis=0).values[0][0]

    def test_multi_index_df_to_component_dfs(self):
        mi_df_index = pd.MultiIndex.from_arrays(
            [["D", "E"], [-666, -666], ["dd", "ee"]],
            names=["rid", "rhd1", "rhd2"])
        mi_df_columns = pd.MultiIndex.from_arrays(
            [["A", "B", "C"], [1, 2, 3], ["Z", "Y", "X"]],
            names=["cid", "chd1", "chd2"])
        mi_df = pd.DataFrame(
            [[1, 3, 5], [7, 11, 13]],
            index=mi_df_index, columns=mi_df_columns)

        e_row_metadata_df = pd.DataFrame(
            [[-666, "dd"], [-666, "ee"]],
            index=pd.Index(["D", "E"], name="rid"),
            columns=pd.Index(["rhd1", "rhd2"], name="rhd"))
        e_col_metadata_df = pd.DataFrame(
            [[1, "Z"], [2, "Y"], [3, "X"]],
            index=pd.Index(["A", "B", "C"], name="cid"),
            columns=pd.Index(["chd1", "chd2"], name="chd"))
        e_data_df = pd.DataFrame(
            [[1, 3, 5], [7, 11, 13]],
            index=pd.Index(["D", "E"], name="rid"),
            columns=pd.Index(["A", "B", "C"], name="cid"))

        (data_df, row_df, col_df) = GCToo.multi_index_df_to_component_dfs(mi_df)

        self.assertTrue(col_df.equals(e_col_metadata_df))
        self.assertTrue(row_df.equals(e_row_metadata_df))
        self.assertTrue(data_df.equals(e_data_df))

        # edge case: if the index (or column) of the multi-index has only one
        # level, it becomes a regular index
        mi_df_index_plain = pd.MultiIndex.from_arrays(
            [["D", "E"]], names=["rid"])
        mi_df2 = pd.DataFrame(
            [[1, 3, 5], [7, 11, 13]],
            index=mi_df_index_plain, columns=mi_df_columns)

        # row df should be empty
        e_row_df2 = pd.DataFrame(index=["D", "E"])

        (data_df2, row_df2, col_df2) = GCToo.multi_index_df_to_component_dfs(mi_df2)
        self.assertTrue(row_df2.equals(e_row_df2))
        self.assertTrue(col_df2.equals(e_col_metadata_df))
        self.assertTrue(data_df2.equals(e_data_df))


if __name__ == "__main__":
    setup_GCToo_logger.setup(verbose=True)

    unittest.main()


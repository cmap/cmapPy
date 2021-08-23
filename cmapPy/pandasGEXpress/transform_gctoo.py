"""
transform_gctoo.py

module to contain various transformations of GCToo objects.  Initially just transpose.

"""
import logging

import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import cmapPy.pandasGEXpress.GCToo as GCToo


logger = logging.getLogger(setup_logger.LOGGER_NAME)

def transpose(my_gctoo):
    new_gctoo = GCToo.GCToo(
        data_df=my_gctoo.data_df.T,
        row_metadata_df=my_gctoo.col_metadata_df,
        col_metadata_df=my_gctoo.row_metadata_df
    )

    return new_gctoo
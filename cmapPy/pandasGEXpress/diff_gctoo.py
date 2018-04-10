'''
diff_gctoo.py

Given a GCToo object calculates differential values (expression, viability etc.)
'''
import sys
import cmapPy.math.robust_zscore as robust_zscore
import cmapPy.pandasGEXpress.GCToo as GCToo

def calc_differential(gctoo, plate_control=True, group_field='pert_type', group_val='ctl_vehicle', func = robust_zscore.calc_zscore):

    '''
    :param df (pandas df):
    :param plate_control (bool): True means calculate differential using plate control. False means vehicle control.
    :param group_field (string): Metadata field in which to find group_val
    :param group_val (string): Value in group_field that indicates use in vehicle control
    :param func (function): Function to apply to data fro calculating diff, eg. zscore, fold change
    :return zscore_gctoo (pandas df): Zscored data!
    '''

    if plate_control == False:
        # If using only a subset of the plate for control (usually vehicle control) extract this df
        neg_dex = gctoo.col_metadata_df[gctoo.col_metadata_df[group_field] == group_val].index.tolist()
        neg_df = gctoo.data_df[neg_dex]
        zscore_data = func(gctoo.data_df, neg_df)

    elif plate_control == True:
        zscore_data = func(gctoo.data_df)

    row_metadata_df = gctoo.row_metadata_df

    # Threshold zscore data before returning
    zscore_data[zscore_data < -10] = -10
    zscore_data[zscore_data > 10] = 10

    zscore_gctoo = GCToo.GCToo(data_df=zscore_data, row_metadata_df=row_metadata_df, col_metadata_df=gctoo.col_metadata_df)

    return zscore_gctoo
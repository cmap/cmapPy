'''
diff_gctoo.py

Given a GCToo object calculates differential values (expression, viability etc.)
Values can be made differential relative to all samples on a plate ("plate-control")
or relative to negative control samples ("vehicle-control").
'''
import sys
import cmapPy.math.robust_zscore as robust_zscore
import cmapPy.pandasGEXpress.GCToo as GCToo

def calc_differential(gctoo, plate_control=True, group_field='pert_type', group_val='ctl_vehicle',
                      func = robust_zscore.calc_zscore, pos_diff_thresh=10, neg_diff_thresh=-10):

    '''
    Args:
    df (pandas df): data on which to perform diff
    plate_control (bool): True means calculate differential using plate control. False means vehicle control.
    group_field (string): Metadata field in which to find group_val
    group_val (string): Value in group_field that indicates use in vehicle control
    func (function): Function to apply to data for calculating diff, eg. zscore, fold change
    pos_diff_thresh (float): Maximum value for diff data
    neg_diff_thresh: Minimum value for diff data

    Returns:
    diff_gctoo (pandas df): Diff data!
    '''

    if plate_control == False:
        # If using only a subset of the plate for control (usually vehicle control) extract this df
        neg_dex = gctoo.col_metadata_df[gctoo.col_metadata_df[group_field] == group_val].index.tolist()
        neg_df = gctoo.data_df[neg_dex]
        diff_data = func(gctoo.data_df, neg_df)

    elif plate_control == True:
        diff_data = func(gctoo.data_df)

    row_metadata_df = gctoo.row_metadata_df

    # Threshold zscore data before returning
    diff_data[diff_data < neg_diff_thresh] = neg_diff_thresh
    diff_data[diff_data > pos_diff_thresh] = pos_diff_thresh

    diff_gctoo = GCToo.GCToo(data_df=diff_data, row_metadata_df=row_metadata_df, col_metadata_df=gctoo.col_metadata_df)

    return diff_gctoo
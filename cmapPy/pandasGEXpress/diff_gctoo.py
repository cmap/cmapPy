'''
diff_gctoo.py

Converts a matrix of values (e.g. gene expression, viability, etc.) into a
matrix of differential values. Values can be made differential relative to all
samples in the dataset ("plate-control") or relative to just negative control
samples ("vehicle-control"). The method of computing the differential can be
either a robust z-score ("robust_z") or simply median normalization
("median_norm").

'''
import cmapPy.math.robust_zscore as robust_zscore
import cmapPy.pandasGEXpress.GCToo as GCToo

possible_diff_methods = ["robust_z", "median_norm"]


def diff_gctoo(gctoo, plate_control=True, group_field='pert_type', group_val='ctl_vehicle',
               diff_method="robust_z", upper_diff_thresh=10, lower_diff_thresh=-10):
    ''' Converts a matrix of values (e.g. gene expression, viability, etc.)
    into a matrix of differential values.

    Args:
    df (pandas df): data to make diff_gctoo
    plate_control (bool): True means calculate diff_gctoo using plate control.
        False means vehicle control.
    group_field (string): Metadata field in which to find group_val
    group_val (string): Value in group_field that indicates use in vehicle control
    diff_method (string): Method of computing differential data; currently only
        support either "robust_z" or "median_norm"
    upper_diff_thresh (float): Maximum value for diff data
    lower_diff_thresh (float): Minimum value for diff data

    Returns:
    out_gctoo (GCToo object): GCToo with differential data values
    '''
    assert diff_method in possible_diff_methods, (
        "possible_diff_methods: {}, diff_method: {}".format(
            possible_diff_methods, diff_method))

    # Compute median and MAD using all samples in the dataset
    if plate_control:

        # Compute differential data
        if diff_method == "robust_z":
            diff_data = robust_zscore.robust_zscore(gctoo.data_df)

        elif diff_method == "median_norm":
            medians = gctoo.data_df.median(axis=1)
            diff_data = gctoo.data_df.subtract(medians, axis='index')

    # Compute median and MAD from negative controls, rather than all samples
    else:

        assert group_field in gctoo.col_metadata_df.columns.values, (
            "group_field {} not present in column metadata. " +
            "gctoo.col_metadata_df.columns.values: {}").format(
            group_field, gctoo.col_metadata_df.columns.values)

        assert sum(gctoo.col_metadata_df[group_field] == group_val) > 0, (
            "group_val {} not present in the {} column.").format(
            group_val, group_field)

        # Find negative control samples
        neg_ctl_samples = gctoo.col_metadata_df.index[gctoo.col_metadata_df[group_field] == group_val]
        neg_ctl_df = gctoo.data_df[neg_ctl_samples]

        # Compute differential data
        if diff_method == "robust_z":
            diff_data = robust_zscore.robust_zscore(gctoo.data_df, neg_ctl_df)

        elif diff_method == "median_norm":
            medians = gctoo.data_df.median(axis=1)
            diff_data = gctoo.data_df.subtract(medians, axis='index')

    # Threshold differential data before returning
    diff_data = diff_data.clip(lower=lower_diff_thresh, upper=upper_diff_thresh)

    # Construct output GCToo object
    out_gctoo = GCToo.GCToo(data_df=diff_data,
                            row_metadata_df=gctoo.row_metadata_df,
                            col_metadata_df=gctoo.col_metadata_df)

    return out_gctoo


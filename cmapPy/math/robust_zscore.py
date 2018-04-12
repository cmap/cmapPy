'''
robust_zscore.py

Given a pandas df, and an optional control df, will calculate zscores using plate control or vehicle control
Values can be zscored relative to all samples on a plate ("plate-control")
or relative to negative control samples ("vehicle-control").
'''
rounding_precision = 4
def calc_zscore(mat, ctrl_mat=None, min_mad=.1):
    '''
    Args:
    mat (pandas df): Matrix of data that zscoring will be applied to
    ctrl_mat (pandas df): Optional subset matrix from which to draw medians and MADS (vehicle control)

    Returns:
    zscore_data (pandas_df): Zscored data!
    '''

    # If optional df exists, calc medians and mads from it
    if ctrl_mat is not None:
        medians = ctrl_mat.median(axis=1)
        median_devs = abs(ctrl_mat.subtract(medians, axis=0))

    # Else just use plate medians
    else:
        medians = mat.median(axis=1)
        median_devs = abs(mat.subtract(medians, axis=0))

    sub = mat.subtract(medians, axis='index')
    mads = median_devs.median(axis=1)

    # Threshold mads
    mads[mads < min_mad] = min_mad
    # Must multiply values by 1.4826 to make MAD comparable to SD (https://en.wikipedia.org/wiki/Median_absolute_deviation)
    zscore_data = sub.divide(mads * 1.4826, axis='index')

    return zscore_data.round(rounding_precision)
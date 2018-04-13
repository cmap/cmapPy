'''
robust_zscore.py

Robustly z-scores a pandas df along the rows (i.e. the z-score is made relative
to a row). A robust z-score means that median is used instead of mean and
median absolute deviation (MAD) instead of standard deviation in the
standard z-score calculation:

z = (x - u) / s

x: input value
u: median
s: MAD

Optionally, the median and MAD can be computed from a control df, instead of the
input df. This functionality is useful for "vehicle-control"; that is, if
the control df consists only of negative control samples, the median and MAD
can be computed using just those samples but applied to the input df.
'''

rounding_precision = 4


def robust_zscore(mat, ctrl_mat=None, min_mad=0.1):
    ''' Robustly z-score a pandas df along the rows.

    Args:
    mat (pandas df): Matrix of data that z-scoring will be applied to
    ctrl_mat (pandas df): Optional matrix from which to compute medians and MADs
        (e.g. vehicle control)
    min_mad (float): Minimum MAD to threshold to; tiny MAD values will cause
        z-scores to blow up

    Returns:
    zscore_df (pandas_df): z-scored data
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
    mads = mads.clip(lower=min_mad)

    # Must multiply values by 1.4826 to make MAD comparable to SD
    # (https://en.wikipedia.org/wiki/Median_absolute_deviation)
    zscore_df = sub.divide(mads * 1.4826, axis='index')

    return zscore_df.round(rounding_precision)
def zscore(mat, ctrl_mat=None):

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
    mads[mads < .1] = .1
    zscore_data = sub.divide(mads * 1.4826, axis='index')

    return zscore_data
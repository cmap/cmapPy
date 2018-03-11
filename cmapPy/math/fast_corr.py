import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import numpy
import cmapPy.math.fast_cov as fast_cov


logger = logging.getLogger(setup_logger.LOGGER_NAME)


def fast_corr(x, y=None, axis=0, do_print_trace=False):
    """calculate the correlation matrix for x, or optionally, the correlaton matrix between x and y.
    axis parameter defines whether to treat the rows or columns as vectors that the covariance is calculated
    between

    Args:
        x (numpy array-like) NxM in shape
        y (numpy array-like) OxP in shape
        axis (integer) indicates which axis of the arrays is the vectors.  axis=0 indicates calculate
            the covariance between the rows, axis=1 indicates calculate the covariance between the columns
        do_print_trace (bool) whether or not to use logger.debug to print out intermediate mathematical steps
            (WARNING: will print out all intermediate matrices, potentially lots of output!)

        returns (numpy array-like) QxR array of the covariance values
            for defaults (y=None, axis=0), shape is NxN
            if y=None and axis=1, shape is MxM
            if y is provied, axis=0, shape is NxO (and P==M in other words number of columns in x & y are the same)
            if y is provided, axis=1, shape is MxP (and N==O in other words number of rows in x & y are the same)
    """
    if y is None:
        y = x

    cov_mat = fast_cov.fast_cov(x, y, axis, do_print_trace)
    if do_print_trace:  logger.debug("cov_mat:\n{}".format(cov_mat))
    
    std_x = numpy.std(x.T, axis=axis, ddof=1)
    if do_print_trace:  logger.debug("std_x:\n{}".format(std_x))
    std_y = numpy.std(y.T, axis=axis, ddof=1)
    if do_print_trace:  logger.debug("std_y:\n{}".format(std_y))
    
    std_outer = numpy.outer(std_x, std_y)
    if do_print_trace:  logger.debug("std_outer:\n{}".format(std_outer))

    return cov_mat / std_outer

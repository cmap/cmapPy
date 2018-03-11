import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import numpy


logger = logging.getLogger(setup_logger.LOGGER_NAME)


def fast_cov(x, y=None, axis=0, do_print_trace=False):
    """calculate the covariance matrix for x, or optionally, the covariance matrix between x and y.
    axis parameter defines whether to treat the rows or columns as vectors that the correlation is calculated
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
    validate_axis(axis)
    validate_x_y(x, y, axis)

    if y is None:
        y = x

    mean_x = numpy.mean(x.T, axis=axis)
    if do_print_trace:  logger.debug("mean_x:\n{}".format(mean_x))
    mean_y = numpy.mean(y.T, axis=axis)
    if do_print_trace:  logger.debug("mean_y:\n{}".format(mean_y))
    
    mean_centered_x = (x.T - mean_x).T if axis == 0 else (x - mean_x).T
    if do_print_trace:  logger.debug("mean_centered_x:\n{}".format(mean_centered_x))
    mean_centered_y = y.T - mean_y if axis == 0 else y - mean_y
    if do_print_trace:  logger.debug("mean_centered_y:\n{}".format(mean_centered_y))
    
    dotprod = numpy.dot(mean_centered_x, mean_centered_y)
    if do_print_trace:  logger.debug("dotprod:\n{}".format(dotprod))
    
    other_axis = 1 if axis == 0 else 0
    if do_print_trace:  logger.debug("other_axis:\n{}".format(other_axis))

    denom = float(x.shape[other_axis] - 1)
    if do_print_trace:  logger.debug("denom:\n{}".format(denom))

    return dotprod / denom


def validate_axis(axis):
    if not (0 == axis or 1 == axis):
        raise CmapPyMathFastCovInvalidInputAxis("invalid value for axis provided to fast_cov - axis:  {}".format(axis))


def validate_x_y(x, y, axis):
    error_msg = ""

    if not hasattr(x, "shape"):
        error_msg += "x needs to be numpy array-like but it does not have \"shape\" attribute - type(x):  {}\n".format(type(x))
    
    if y is not None:
        if not hasattr(y, "shape"):
            error_msg += "y needs to be numpy array-like but it does not have \"shape\" attribute - type(y):  {}\n".format(type(y))
        else:
            base_msg = "with axis={} (finding the covariance between {}), the number of {} in x and y must be the same but they are not - x.shape:  {}  y.shape:  {}\n"
            if 0 == axis:
                if x.shape[1] != y.shape[1]:
                    error_msg += base_msg.format(axis, "rows", "columns", x.shape, y.shape)
            else:
                if x.shape[0] != y.shape[0]:
                    error_msg += base_msg.format(axis, "columns", "rows", x.shape, y.shape)

    if error_msg != "":
        raise CmapPyMathFastCovInvalidInputXY(error_msg)


class CmapPyMathFastCovInvalidInputAxis(Exception):
    pass

class CmapPyMathFastCovInvalidInputXY(Exception):
    pass
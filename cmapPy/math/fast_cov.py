import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import numpy


logger = logging.getLogger(setup_logger.LOGGER_NAME)


def _fast_dot_divide(x, y, destination):
    """helper method for use within the _fast_cov method - carry out the dot product and subsequent 
    division to generate the covariance values.  For use when there are no missing values.
    """
    numpy.dot(x.T, y, out=destination)
    numpy.divide(destination, (x.shape[0] - 1), out=destination)


def calculate_non_mask_overlaps(x_mask, y_mask):
    """for two mask arrays (x_mask, y_mask - boolean arrays) determine the number of entries in common there would be for each 
    entry if their dot product were taken
    """
    x_is_not_nan = 1 * ~x_mask
    y_is_not_nan = 1 * ~y_mask

    r = numpy.dot(x_is_not_nan.T, y_is_not_nan)
    return r


def _nan_dot_divide(x, y, destination):
    """helper method for use within the _fast_cov method - carry out the dot product and subsequent
    division to generate the covariance values.  For use when there are missing values.
    """
    numpy.ma.dot(x.T, y, out=destination)

    divisor = calculate_non_mask_overlaps(x.mask, y.mask) - 1

    numpy.ma.divide(destination, divisor, out=destination)


def fast_cov(x, y=None, destination=None):
    """calculate the covariance matrix for the columns of x (MxN), or optionally, the covariance matrix between the
    columns of x and and the columns of y (MxP).  (In the language of statistics, the columns are variables, the rows
    are observations).

    Args:
        x (numpy array-like) MxN in shape
        y (numpy array-like) MxP in shape
        destination (numpy array-like) optional location where to store the results as they are calculated (e.g. a numpy
            memmap of a file)

        returns (numpy array-like) array of the covariance values
            for defaults (y=None), shape is NxN
            if y is provided, shape is NxP
    """
    r = _fast_cov(numpy.mean, _fast_dot_divide, x, y, destination)

    return r


def _fast_cov(mean_method, dot_divide_method, x, y, destination):
    validate_inputs(x, y, destination)

    if y is None:
        y = x

    if destination is None:
        destination = numpy.zeros((x.shape[1], y.shape[1]))

    mean_x = mean_method(x, axis=0)
    mean_y = mean_method(y, axis=0)

    mean_centered_x = (x - mean_x).astype(destination.dtype)
    mean_centered_y = (y - mean_y).astype(destination.dtype)
    
    dot_divide_method(mean_centered_x, mean_centered_y, destination)

    return destination


def validate_inputs(x, y, destination):
    error_msg = ""

    if not hasattr(x, "shape"):
        error_msg += "x needs to be numpy array-like but it does not have \"shape\" attribute - type(x):  {}\n".format(type(x))
    
    if destination is not None and not hasattr(destination, "shape"):
        error_msg += "destination needs to be numpy array-like but it does not have \"shape\" attribute - type(destination):  {}\n".format(type(destination))

    if y is None:
        if destination is not None:
            expected_shape = (x.shape[1], x.shape[1])
            if destination.shape != expected_shape:
                error_msg += "x and destination provided, therefore destination must have shape matching number of columns of x but it does not - x.shape:  {}  expected_shape:  {}  destination.shape:  {}\n".format(
                    x.shape, expected_shape, destination.shape)
    else:
        if not hasattr(y, "shape"):
            error_msg += "y needs to be numpy array-like but it does not have \"shape\" attribute - type(y):  {}\n".format(type(y))
        elif x.shape[0] != y.shape[0]:
            error_msg += "the number of rows in the x and y matrices must be the same - x.shape:  {}  y.shape:  {}\n".format(x.shape, y.shape)
        elif destination is not None:
            expected_shape = (x.shape[1], y.shape[1])
            if destination.shape != expected_shape:
                error_msg += "x, y, and destination provided, therefore destination must have number of rows matching number of columns of x and destination needs to have number of columns matching number of columns of y - x.shape:  {}  y.shape:  {}  expected_shape:  {}  destination.shape:  {}\n".format(
                    x.shape, y.shape, expected_shape, destination.shape)

    if error_msg != "":
        raise CmapPyMathFastCovInvalidInputXY(error_msg)


def nan_fast_cov(x, y=None, destination=None):
    """calculate the covariance matrix (ignoring nan values) for the columns of x (MxN), or optionally, the covariance matrix between the
    columns of x and and the columns of y (MxP).  (In the language of statistics, the columns are variables, the rows
    are observations).

    Args:
        x (numpy array-like) MxN in shape
        y (numpy array-like) MxP in shape
        destination (numpy masked array-like) optional location where to store the results as they are calculated (e.g. a numpy
            memmap of a file)

        returns (numpy array-like) array of the covariance values
            for defaults (y=None), shape is NxN
            if y is provided, shape is NxP
    """
    x_masked = numpy.ma.array(x, mask=numpy.isnan(x))

    if y is None:
        y_masked = x_masked
    else:
        y_masked = numpy.ma.array(y, mask=numpy.isnan(y))

    dest_was_None = False
    if destination is None:
        destination = numpy.ma.zeros((x_masked.shape[1], y_masked.shape[1]))
        dest_was_None = True

    r = _fast_cov(numpy.nanmean, _nan_dot_divide, x_masked, y_masked, destination)

    r[numpy.isinf(r)] = numpy.nan

    r = numpy.ma.filled(r, fill_value=numpy.nan) if dest_was_None else r

    return r


class CmapPyMathFastCovInvalidInputXY(Exception):
    pass

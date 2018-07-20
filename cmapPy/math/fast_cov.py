import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import numpy


logger = logging.getLogger(setup_logger.LOGGER_NAME)


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
    validate_inputs(x, y, destination)

    if y is None:
        y = x

    if destination is None:
        destination = numpy.zeros((x.shape[1], y.shape[1]))

    mean_x = numpy.mean(x, axis=0)
    mean_y = numpy.mean(y, axis=0)

    mean_centered_x = (x - mean_x).astype(destination.dtype)
    mean_centered_y = (y - mean_y).astype(destination.dtype)
    
    numpy.dot(mean_centered_x.T, mean_centered_y, out=destination)
    numpy.divide(destination, (x.shape[0] - 1), out=destination)

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


class CmapPyMathFastCovInvalidInputXY(Exception):
    pass

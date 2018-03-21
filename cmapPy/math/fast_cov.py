import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import numpy


logger = logging.getLogger(setup_logger.LOGGER_NAME)


def fast_cov(x, y=None):
    """calculate the covariance matrix for the columns of x (MxN), or optionally, the covariance matrix between the
    columns of x and and the columns of y (MxP).  (In the language of statistics, the columns are variables, the rows
    are observations).

    Args:
        x (numpy array-like) MxN in shape
        y (numpy array-like) MxP in shape

        returns (numpy array-like) array of the covariance values
            for defaults (y=None), shape is NxN
            if y is provided, shape is NxP
    """
    validate_x_y(x, y)

    if y is None:
        y = x

    mean_x = numpy.mean(x, axis=0)    
    mean_y = numpy.mean(y, axis=0)

    mean_centered_x = x - mean_x
    mean_centered_y = y - mean_y
    
    dotprod = numpy.dot(mean_centered_x.T, mean_centered_y)

    denom = x.shape[0] - 1

    return dotprod / denom


def validate_x_y(x, y):
    error_msg = ""

    if not hasattr(x, "shape"):
        error_msg += "x needs to be numpy array-like but it does not have \"shape\" attribute - type(x):  {}\n".format(type(x))
    
    if y is not None:
        if not hasattr(y, "shape"):
            error_msg += "y needs to be numpy array-like but it does not have \"shape\" attribute - type(y):  {}\n".format(type(y))
        elif x.shape[0] != y.shape[0]:
            error_msg += "the number of rows in the x and y matrices must be the same".format(x.shape, y.shape)

    if error_msg != "":
        raise CmapPyMathFastCovInvalidInputXY(error_msg)


class CmapPyMathFastCovInvalidInputAxis(Exception):
    pass

class CmapPyMathFastCovInvalidInputXY(Exception):
    pass
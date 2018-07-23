import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import numpy
import cmapPy.math.fast_cov as fast_cov
import pandas


logger = logging.getLogger(setup_logger.LOGGER_NAME)


def fast_corr(x, y=None, destination=None):
    """calculate the pearson correlation matrix for the columns of x (with dimensions MxN), or optionally, the pearson correlaton matrix
    between x and y (with dimensions OxP).  If destination is provided, put the results there.  
    In the language of statistics the columns are the variables and the rows are the observations.

    Args:
        x (numpy array-like) MxN in shape
        y (optional, numpy array-like) OxP in shape.  M (# rows in x) must equal O (# rows in y)
        destination (numpy array-like) optional location where to store the results as they are calculated (e.g. a numpy
            memmap of a file)

        returns (numpy array-like) array of the covariance values
            for defaults (y=None), shape is NxN
            if y is provied, shape is NxP
    """
    if y is None:
        y = x

    r = fast_cov.fast_cov(x, y, destination)

    std_x = numpy.std(x, axis=0, ddof=1)
    std_y = numpy.std(y, axis=0, ddof=1)

    numpy.divide(r, std_x[:, numpy.newaxis], out=r)
    numpy.divide(r, std_y[numpy.newaxis, :], out=r)

    return r


def fast_spearman(x, y=None, destination=None):
    """calculate the spearman correlation matrix for the columns of x (with dimensions MxN), or optionally, the spearman correlaton
    matrix between the columns of x and the columns of y (with dimensions OxP).  If destination is provided, put the results there.
    In the language of statistics the columns are the variables and the rows are the observations.

    Args:
        x (numpy array-like) MxN in shape
        y (optional, numpy array-like) OxP in shape.  M (# rows in x) must equal O (# rows in y)
        destination (numpy array-like) optional location where to store the results as they are calculated (e.g. a numpy
            memmap of a file)

        returns:
            (numpy array-like) array of the covariance values
                for defaults (y=None), shape is NxN
                if y is provied, shape is NxP
    """
    logger.debug("x.shape:  {}".format(x.shape))
    if hasattr(y, "shape"):  
        logger.debug("y.shape:  {}".format(y.shape))

    x_ranks = pandas.DataFrame(x).rank(method="average").values
    logger.debug("some min and max ranks of x_ranks:\n{}\n{}".format(numpy.min(x_ranks[:10], axis=0), numpy.max(x_ranks[:10], axis=0)))

    y_ranks = pandas.DataFrame(y).rank(method="average").values if y is not None else None

    return fast_corr(x_ranks, y_ranks, destination)

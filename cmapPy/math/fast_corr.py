import logging
import cmapPy.pandasGEXpress.setup_GCToo_logger as setup_logger
import numpy
import cmapPy.math.fast_cov as fast_cov
import pandas


logger = logging.getLogger(setup_logger.LOGGER_NAME)


def fast_corr(x, y=None):
    """calculate the pearson correlation matrix for the columns of x (MxN), or optionally, the correlaton matrix between x and y (OxP).
    In the language of statistics the columns are the variables and the rows are the observations.

    Args:
        x (numpy array-like) MxN in shape
        y (optional, numpy array-like) OxP in shape

        returns (numpy array-like) array of the covariance values
            for defaults (y=None), shape is NxN
            if y is provied, shape is NxP
    """
    if y is None:
        y = x

    cov_mat = fast_cov.fast_cov(x, y)
    
    std_x = numpy.std(x, axis=0, ddof=1)
    std_y = numpy.std(y, axis=0, ddof=1)
    
    std_outer = numpy.outer(std_x, std_y)

    return cov_mat / std_outer


def fast_spearman(x, y=None):
    """calculate the spearnab correlation matrix for the columns of x (MxN), or optionally, the spearmancorrelaton matrix between x and y (OxP).
    In the language of statistics the columns are the variables and the rows are the observations.

    Args:
        x (numpy array-like) MxN in shape
        y (optional, numpy array-like) OxP in shape

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

    return fast_corr(x_ranks, y_ranks)

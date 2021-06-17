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
    
    r = fast_cov.fast_cov(x, y, destination=destination)

    std_x = numpy.std(x, axis=0, ddof=1)
    if numpy.isscalar(std_x):
        std_x = numpy.array((std_x,))

    std_y = numpy.std(y, axis=0, ddof=1)
    if numpy.isscalar(std_y):
        std_y = numpy.array((std_y,))

    numpy.divide(r, std_x[:, numpy.newaxis], out=r)
    numpy.divide(r, std_y[numpy.newaxis, :], out=r)

    return r


def calculate_moments_with_additional_mask(x, mask):
    """calculate the moments (y, y^2, and variance) of the columns of x, excluding masked within x, for each of the masking columns in mask
    Number of rows in x and mask must be the same.

    Args:
        x (numpy.ma.array like)
        mask (numpy array-like boolean) 
    """
    non_mask_overlaps = fast_cov.calculate_non_mask_overlaps(x.mask, mask)

    unmask = 1.0 * ~mask
    
    expect_x = numpy.ma.dot(x.T, unmask) / non_mask_overlaps
    expect_x = expect_x.T

    expect_x_squared = numpy.ma.dot(
        numpy.power(x, 2.0).T, unmask
    ) / non_mask_overlaps
    expect_x_squared = expect_x_squared.T

    var_x = (expect_x_squared - numpy.power(expect_x, 2.0)) * non_mask_overlaps.T / (non_mask_overlaps.T - 1)

    return expect_x, expect_x_squared, var_x


def nan_fast_corr(x, y=None, destination=None):
    """calculate the pearson correlation matrix (ignoring nan values) for the columns of x (with dimensions MxN), or optionally, the pearson correlaton matrix
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
    x_masked = numpy.ma.array(x, mask=numpy.isnan(x))

    if y is None:
        y_masked = x_masked
    else:
        y_masked = numpy.ma.array(y, mask=numpy.isnan(y))

    r = fast_cov.nan_fast_cov(x_masked, y_masked, destination=destination)

    # calculate the standard deviation of the columns of each matrix, given the masking from the other
    _, _, var_x = calculate_moments_with_additional_mask(x_masked, y_masked.mask)
    std_x = numpy.sqrt(var_x)

    _, _, var_y = calculate_moments_with_additional_mask(y_masked, x_masked.mask)
    std_y = numpy.sqrt(var_y)

    numpy.divide(r, std_x.T, out=r)
    numpy.divide(r, std_y, out=r)

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
    r = _fast_spearman(fast_corr, x, y, destination)
    return r


def _fast_spearman(corr_method, x, y, destination):
    """internal method for calculating spearman correlation, allowing subsititution of methods for calculationg correlation (corr_method),
    allowing to choose methods that are fast (fast_corr) or tolerant of nan's (nan_fast_corr) to be used
    """
    logger.debug("x.shape:  {}".format(x.shape))
    if hasattr(y, "shape"):  
        logger.debug("y.shape:  {}".format(y.shape))

    x_ranks = pandas.DataFrame(x).rank(method="average", na_option="keep").values
    logger.debug("some min and max ranks of x_ranks:\n{}\n{}".format(numpy.min(x_ranks[:10], axis=0), numpy.max(x_ranks[:10], axis=0)))

    y_ranks = pandas.DataFrame(y).rank(method="average", na_option="keep").values if y is not None else None

    return corr_method(x_ranks, y_ranks, destination=destination)


def nan_fast_spearman(x, y=None, destination=None):
    """calculate the spearman correlation matrix (ignoring nan values) for the columns of x (with dimensions MxN), or optionally, the spearman correlaton
    matrix between the columns of x and the columns of y (with dimensions OxP).  If destination is provided, put the results there.
    In the language of statistics the columns are the variables and the rows are the observations.
    Note that the ranks will be slightly miscalculated in the masked situations leading to slight errors in the spearman rho value.

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
    r = _fast_spearman(nan_fast_corr, x, y, destination)
    return r

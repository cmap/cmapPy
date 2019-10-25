'''
agg_wt_avg.py

Aggregate a matrix of replicate profiles into a single signature using
a weighted average based on the correlation between replicates. That is, if
one replicate is less correlated with the other replicates, its values will
not be weighted as highly in the aggregated signature.

Equivalent to the 'modz' method in mortar.
'''

import numpy as np

rounding_precision = 4


def get_upper_triangle(correlation_matrix):
    ''' Extract upper triangle from a square matrix. Negative values are
    set to 0.

    Args:
    correlation_matrix (pandas df): Correlations between all replicates

    Returns:
    upper_tri_df (pandas df): Upper triangle extracted from
        correlation_matrix; rid is the row index, cid is the column index,
        corr is the extracted correlation value
    '''
    upper_triangle = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(np.bool))

    # convert matrix into long form description
    upper_tri_df = upper_triangle.stack().reset_index(level=1)
    upper_tri_df.columns = ['rid', 'corr']

    # Index at this point is cid, it now becomes a column
    upper_tri_df.reset_index(level=0, inplace=True)

    # Get rid of negative values
    upper_tri_df['corr'] = upper_tri_df['corr'].clip(lower=0)

    return upper_tri_df.round(rounding_precision)


def calculate_weights(correlation_matrix, min_wt):
    ''' Calculate a weight for each profile based on its correlation to other
    replicates. Negative correlations are clipped to 0, and weights are clipped
    to be min_wt at the least.

    Args:
    correlation_matrix (pandas df): Correlations between all replicates
    min_wt (float): Minimum raw weight when calculating weighted average

    Returns:
    raw weights (pandas series):  Mean correlation to other replicates
    weights (pandas series): raw_weights normalized such that they add to 1
    '''
    # fill diagonal of correlation_matrix with np.nan
    np.fill_diagonal(correlation_matrix.values, np.nan)

    # remove negative values
    correlation_matrix = correlation_matrix.clip(lower=0)

    # get average correlation for each profile (will ignore NaN)
    raw_weights = correlation_matrix.mean(axis=1)

    # threshold weights
    raw_weights = raw_weights.clip(lower=min_wt)

    # normalize raw_weights so that they add to 1
    weights = raw_weights / sum(raw_weights)

    return raw_weights.round(rounding_precision), weights.round(rounding_precision)


def agg_wt_avg(mat, min_wt = 0.01, corr_metric='spearman'):
    ''' Aggregate a set of replicate profiles into a single signature using
    a weighted average.

    Args:
    mat (pandas df): a matrix of replicate profiles, where the columns are
        samples and the rows are features; columns correspond to the
        replicates of a single perturbagen
    min_wt (float): Minimum raw weight when calculating weighted average
    corr_metric (string): Spearman or Pearson; the correlation method

    Returns:
    out_sig (pandas series): weighted average values
    upper_tri_df (pandas df): the correlations between each profile that went into the signature
    raw weights (pandas series): weights before normalization
    weights (pandas series): weights after normalization
    '''
    assert mat.shape[1] > 0, "mat is empty! mat: {}".format(mat)

    if mat.shape[1] == 1:

        out_sig = mat
        upper_tri_df = None
        raw_weights = None
        weights = None

    else:

        assert corr_metric in ["spearman", "pearson"]

        # Make correlation matrix column wise
        corr_mat = mat.corr(method=corr_metric)

        # Save the values in the upper triangle
        upper_tri_df = get_upper_triangle(corr_mat)

        # Calculate weight per replicate
        raw_weights, weights = calculate_weights(corr_mat, min_wt)

        # Apply weights to values
        weighted_values = mat * weights
        out_sig = weighted_values.sum(axis=1)

    return out_sig, upper_tri_df, raw_weights, weights
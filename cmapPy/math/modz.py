'''
modz.py

modz refers to a weighted average of zscores - but can be applied to other types of data as well
Given a matrix of profiles on which you want to calculate a weighted average, returns a single profile of modz values
Weights are calculated based on the correlation between replicates - so if one replicate is less highly correlated it
will not be weighted as highly in the level 5 signature.
'''

import pandas as pd
import numpy as np
import os
import math

rounding_precision=4

def upper_triangle(correlation_matrix):
    '''
    Args:
    correlation_matrix (pandas df): Correlations between all replicates

    Returns:
    upper_tri_series (pandas series): Upper triangle extracted from corr mat
    '''
    upper_triangle = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(np.bool))

    # convert matrix into long form description
    upper_tri_series = upper_triangle.stack().reset_index(level=1)

    upper_tri_series.columns = ['rid', 'corr']

    # Index at this point is CID, it now becomes a column
    upper_tri_series.reset_index(level=0, inplace=True)

    return upper_tri_series.round(rounding_precision)


def calculate_weights(correlation_matrix, min_wt = 0.01):
    '''
    Args:
    correlation_matrix (pandas df): Correlations between all replicates

    Returns:
    raw weights (pandas series):  Weights computed by summing correlations
    weights (pandas series): Weights computed by summing correlations (raw weights) and then normalized to add to 1 (weights)
    '''

    # fill diagonal of corr_mat with 0s
    np.fill_diagonal(correlation_matrix.values, 0)

    # remove negative values
    correlation_matrix[correlation_matrix < 0] = 0
    raw_weights = correlation_matrix.sum(axis=1) / (len(correlation_matrix.index) - 1)
    raw_weights[raw_weights < min_wt] = min_wt
    weights = raw_weights / sum(raw_weights.abs())

    return raw_weights.round(rounding_precision), weights.round(rounding_precision)


def calc_modz(mat, min_wt = 0.01, corr_metric='spearman'):
    '''
    Args:
    mat (pandas df): a signature matrix, where the columns are samples and the rows are features;
    columns correspond to the replicates of a single perturbagen
    min_wt (float): Minimum raw weight when calculating weighted average
    corr_metric (string): Spearmen or pearson, correlation method

    Returns:
    modz values (pandas series): weighted average values
    upper_tri_series (pandas series): the correlations between each profile that went into the signature
    raw weights (pandas series): weights before normalization to add to 1
    weights (pandas series): weights after normalization
    '''
    # Make correlation matrix column wise
    corr_mat = mat.corr(method=corr_metric)

    # Extract just the values in the upper triangle
    upper_tri_series = upper_triangle(corr_mat)

    # Get rid of negative values
    upper_tri_series['corr'][upper_tri_series['corr'] < 0] = 0

    raw_weights, weights = calculate_weights(corr_mat, min_wt)

    weighted_values = mat * weights

    modz_values = weighted_values.sum(axis=1)

    return modz_values, upper_tri_series, raw_weights, weights
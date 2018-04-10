'''
modz.py

Given a matrix of profiles on which you want to calculate a weighted average, returns a single profile of modz values
'''

import pandas as pd
import numpy as np
import os
import math

def upper_triangle(correlation_matrix):
    '''
    :param correlation_matrix (pandas df): Correlations between all replicates
    :return upper_tri_series (pandas series): Upper triangle extracted from corr mat
    '''
    upper_triangle = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(np.bool))

    # convert matrix into long form description
    upper_tri_series = upper_triangle.stack().reset_index(level=1)

    upper_tri_series.columns = ['rid', 'spearman_corr']

    # Index at this point is CID, it now becomes a column
    upper_tri_series.reset_index(level=0, inplace=True)

    return upper_tri_series.round(4)


def calculate_weights(correlation_matrix):
    '''
    :param correlation_matrix (pandas df): Correlations between all replicates
    :return raw weights, weights (pandas series): Weights computed by summing correlations (raw weights) and then normalized to add to 1 (weights)
    '''

    # fill diagonal of corr_mat with 0s
    np.fill_diagonal(correlation_matrix.values, 0)

    # remove negative values
    correlation_matrix[correlation_matrix < 0] = 0
    raw_weights = correlation_matrix.sum(axis=1) / (len(correlation_matrix.index) - 1)
    raw_weights[raw_weights < .01] = .01
    weights = raw_weights / sum(raw_weights.abs())

    return raw_weights.round(4), weights.round(4)


def main(mat):
    '''
    :param mat (pandas df): One matching profile from each replicate
    :return (4 pandas series): modz values, correlations from upper tri series, raw weights, normalized weights
    '''
    # Make correlation matrix column wise
    corr_mat = mat.corr(method='spearman')

    # Extract just the values in the upper triangle
    upper_tri_series = upper_triangle(corr_mat)

    # Get rid of negative values
    upper_tri_series['spearman_corr'][upper_tri_series['spearman_corr'] < 0] = 0

    raw_weights, weights = calculate_weights(corr_mat)

    weighted_values = mat * weights

    modz_values = weighted_values.sum(axis=1)

    return modz_values, upper_tri_series, raw_weights, weights
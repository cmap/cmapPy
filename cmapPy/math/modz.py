import pandas as pd
import numpy as np
import os
import math

def upper_triangle(correlation_matrix):
    upper_triangle = correlation_matrix.where(np.triu(np.ones(correlation_matrix.shape), k=1).astype(np.bool))

    # convert matrix into long form description
    upper_tri_series = upper_triangle.stack().reset_index(level=1)

    upper_tri_series.columns = ['rid', 'spearman_corr']

    # Index at this point is CID, it now becomes a column
    upper_tri_series.reset_index(level=0, inplace=True)

    return upper_tri_series


def calculate_weights(correlation_matrix):

    np.fill_diagonal(correlation_matrix.values, 0)
    correlation_matrix[correlation_matrix < 0] = 0
    raw_weights = 0.5 * correlation_matrix.sum(axis=1)
    raw_weights[raw_weights < .01] = .01
    weights = raw_weights / sum(raw_weights.abs())

    return raw_weights, weights


def modz(mat):

    corr_mat = mat.corr(method='spearman')

    upper_tri_series = upper_triangle(corr_mat)

    upper_tri_series['spearman_corr'][upper_tri_series['spearman_corr'] < 0] = 0

    raw_weights, weights = calculate_weights(corr_mat)

    weighted_values = mat * weights

    modz_values = weighted_values.sum(axis=1)

    return modz_values, upper_tri_series, raw_weights, weights
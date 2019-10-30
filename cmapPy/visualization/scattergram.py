'''
Created on Sep 30, 2019
@author: Navid Dianati
@contact: navid@broadinstitute.org
'''

import logging
import os

import matplotlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger()


def scattergram(
    df, columns, column_names, title="",
    outfile='',
    fig_dpi=150,
    fontfamily="Roboto"
    ):
    '''
    Make a grid of scatterplots of a set of columns against each other. 
    The values should all be "normalized", i.e., between 0 and 1.
    @param df: Pandas DataFrame containing the variables to be scattered.
    @param columns: list of column names to plot.
    @param column_names: list of display names corresponding to the 
    variable columns.
    @return: g: Seaborn PairGrid object
    '''
    
    df = df.copy()[columns]
    
    # rename the columns
    df.columns = column_names

    df = df.dropna()
    with sns.axes_style('ticks') as c1:
        
        g = sns.PairGrid(
            data=df, vars=column_names,
            palette="Greys", despine=False,
            height=2
            )
        g.map_lower(
            plt.scatter,
            s=10,
            lw=0,
            alpha=0.5,
            color="#555555"
            )
        g.map_diag(
            _plot_hist,
            **dict(
                normed=True,
                alpha=0.5,
                bins=np.linspace(-0.00001, 1.00001, 21),
                histtype="bar",
                edgecolor="#ffffff"
                )
            )
        
        if title:
            g.fig.text(1, 1,
                "{} (N = {:,})".format(title, len(df)),
                fontsize=30,
                fontname=fontfamily,
                fontweight="bold",
                horizontalalignment="right",
                verticalalignment="top"
                )
        
        plt.subplots_adjust(wspace=0, hspace=0.0)
        font_properties = dict(family=fontfamily, weight="bold")
        _adjust_axes(g, font_properties)
        _draw_row_labels(g, column_names)
        
        if outfile:
            plt.savefig(outfile, dpi=fig_dpi)
        return g
    
    
def _adjust_axes(g, font_properties={}):
    for i, j in zip(*np.triu_indices_from(g.axes, 1)):
        g.axes[i, j].set_visible(False)

    for i in range(g.axes.shape[0]):
        for j in range(g.axes.shape[1]):
            ax = g.axes[i, j]
            if i > j:
                ax.set_zorder(100)
                ax.set_xlim(-0.1, 1.1)
                ax.set_ylim(-0.1, 1.1)
                ax.set_ylabel('')
                ax.set_xlabel('')
                frame_line_width = 2
                _set_axis_thickness(ax, frame_line_width)
                ax.xaxis.set_tick_params(width=frame_line_width)
                ax.yaxis.set_tick_params(width=frame_line_width)
                _set_ticks_fontproperties(ax, font_properties)
    for i in range(g.axes.shape[0]):
        ax = g.axes[i, i]
        ax.set_ylim(-0.1, 1.1)
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylabel('')
        ax.set_xlabel('')
        ax.set_yticks([0, 0.5, 1])
        ax.set_xticks([0, 0.5, 1])
        _set_axis_thickness(ax, 1)
        _set_axis_style(ax, '--')
        _set_ticks_fontproperties(ax, font_properties)


def _draw_row_labels(g, column_names):
    for i in range(g.axes.shape[0]):
        label = column_names[i]
        ax = g.axes[i, i]
        ax.annotate(label, (0.5, .5),
                horizontalalignment="center",
                verticalalignment="center",
                fontweight="bold",
                fontname="Roboto",
                fontsize=18,
                zorder=100,
#                     bbox=dict(boxstyle="square,pad=0.5", fc="white", ec="#dddddd", lw=0)
               ) 


def _set_axis_thickness(ax, width):
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linewidth(width)


def _set_axis_style(ax, linestyle):
    for axis in ['top', 'bottom', 'left', 'right']:
        ax.spines[axis].set_linestyle(linestyle)


def _plot_hist(data, **kwargs):
    plt.hist(data, clip_on=True, **kwargs)


def _set_ticks_fontproperties(ax, font_properties):
    ax.set_xticklabels(ax.get_xticks(), font_properties)
    ax.set_yticklabels(ax.get_yticks(), font_properties)


def plot_selected_points_among_all(*args, **kwargs):
    '''
    Legacy function.
    '''
    return scattergram(*args, **kwargs)



'''
Created on Sep 30, 2019

@author: Navid Dianati
@contact: navid@broadinstitute.org
'''
import logging

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger()

figure_dpi = 150


ANNOTATION_KWARGS = dict(
        zorder=100
    )

def stratogram(
    data,
    category_definition,
    category_label,
    category_order,
    metrics,
    column_display_names,
    outfile='',
    bins=51,
    colors=["#9b59b6", "#3498db", "#95a5a6", "#e74c3c", "#34495e", "#2ecc71"] * 3,
    figsize=(40, 20),
    xtick_orientation="horizontal",
    ylabel_fontsize=25,
    xlabel_fontsize=25,
    xlabel_fontcolor="#555555",
    ylabel_fontcolor="#555555",
    fontfamily="Roboto"
):    
    '''
    Create a stratogram of the data. A stratogram is a grid of histograms
    of various metrics computed for a set of data points, stratified by a
    "category_definition" variable. Each column of the grid is one metric, and each row
    depicts a stratum of the data.
    @param data: Pandas DataFrame where each row is a data point and the
    metrics and other variables are in the columns.
    @param category_definition: string name of the column that defines the stratum/
    category of each data point.
    @param category_label: string name of the column that defines the stratum/
    label for each data point.
    @param category_order: string name of the integer column that defines
    the order in which each stratum should be plotted in the rows. There
    should be a one-to-one map between the category_definition and category_order
    variables. 
    @param metrics: list of column names containing numberical values
    whose histogram is plotted.
    @param column_display_names: list of display names for the metrics.
    @keyword outfile: filename to export the figure.
    @keyword bins: number of bins to use for histogram. Same for all cells.
    @keyword colors: list of colors. Each color will be plotted using one
    of these colors, in order.
    @keyword figsize
    @keyword xtick_orientation: Either "horizontal" or "vertical"
    @keyword ylabel_fontsize
    @keyword xlabel_fontsize
    @keyword xlabel_fontcolor
    @keyword ylabel_fontcolor
    @keyword fontfamily
    '''
    df = data.copy()
    column_display_names = [name + "\n" for name in column_display_names]
    
    # Make sure necessary columns are in the dataframe
    assert category_definition in df.columns
    assert category_order in df.columns

    logger.info('Validating the table')
    for metric in metrics:
        assert metric in df.columns, metric

    # Update category_definition order to "remove" non-existent categories
    dict_new_order = {x:i for i, x in  enumerate(sorted(df[category_order].unique().tolist()))}
    df[category_order] = df[category_order].apply(lambda x:dict_new_order[x])
    n_rows = df[category_order].nunique()
    
    n_cols = len(metrics)
    plt.figure(figsize=figsize, dpi=figure_dpi)
    gs = gridspec.GridSpec(n_rows, n_cols)
    gs.update(wspace=0.0, hspace=0.0)
    
    # Count the total number of test compounds
    test_categories = [c for c in df[category_definition].dropna().unique() if is_test_category(c)]
    num_test_compounds = len(df[df[category_definition].isin(test_categories)])
    
    # Group the data by the category_definition variable and for each stratum
    # Plot a row of histograms in the grid.
    grouped = df.groupby(category_definition)
    for name, group in grouped:
        row_is_test_compounds = is_test_category(name)
        name = group[category_label].unique()
        assert len(name) == 1
        name = name[0]
            
        group.name = name
        row_label = name
        n_points = len(group)
        fraction_of_tests = float(n_points) / num_test_compounds
        
        if row_is_test_compounds:
            row_sublabel = "(n={:,} - {:.0%} of test)".format(n_points, fraction_of_tests)
        else:
            row_sublabel = "(n={:,})".format(n_points)
        plot_row_of_histograms(
            group,
            gs,
            category_order,
            n_rows,
            n_cols,
            plot_columns=metrics,
            column_display_names=column_display_names,
            bins=bins,
            row_label=row_label,
            row_sublabel=row_sublabel,
            fontfamily=fontfamily,
            colors=colors,
            xtick_orientation=xtick_orientation,
            ylabel_fontsize=ylabel_fontsize,
            xlabel_fontsize=xlabel_fontsize,
            xlabel_fontcolor=xlabel_fontcolor,
            ylabel_fontcolor=ylabel_fontcolor,
            )
    
    if outfile:
        plt.savefig(outfile, bbox_inches='tight')


def is_test_category(category):
    '''Determine from the category st ring
    whether this is a test compound category'''
    return 'test' in category.lower()


def get_axis_size(ax):
    bbox = ax.get_window_extent().transformed(plt.gcf().dpi_scale_trans.inverted())
    width, height = bbox.width, bbox.height
    return width, height


def _add_annotation_reproducibility(ax, data, metric_label, col_id, row_id, threshold=0.2, **kwargs):
    logger.info("Adding annotation for column {}".format(metric_label))
    ylim = ax.get_ylim()
    n_points = len(data)
    n_pass = len(data[data >= threshold])
    width, height = get_axis_size(ax)
    fontsize = int(height * figure_dpi * 0.08)
    ax.plot([threshold, threshold], ylim, '--', color="#aaaaaa", alpha=0.5)
    
    if row_id == 0:
        # In data coordinates
        ax.text(threshold, ylim[1] * 1.1, "{:.2f}".format(threshold),
                horizontalalignment="center",
                verticalalignment="bottom",
                fontsize=fontsize * 0.8,
                fontweight="bold",
                fontname=kwargs.get('fontfamily'),
                color="#aaaaaa",
                )
    if n_points == 0:
        return
    ax.text(0.95, 0.9, ">{:.2f} : n={:,}\n({:.0%})".format(threshold, n_pass, float(n_pass) / n_points),
            horizontalalignment="right",
            verticalalignment="top",
            fontsize=fontsize,
            color="#222222",
            fontweight="bold",
            fontname=kwargs.get('fontfamily'),
            transform=ax.transAxes,
            **ANNOTATION_KWARGS
            )
    pass


def _add_annotation_recall(ax, data, metric_label, col_id, row_id, **kwargs):
    logger.info("Adding annotation for column {}".format(metric_label))
    ylim = ax.get_ylim()
    n_points = len(data)
    
    threshold = 0.05
    
    n_pass = len(data[data <= threshold])
    width, height = get_axis_size(ax)
    fontsize = int(height * figure_dpi * 0.08)
    ax.plot([threshold, threshold], ylim, '--', color="#aaaaaa", alpha=0.5)
  
    if row_id == 0:
        # In data coordinates
        ax.text(
            threshold, ylim[1] * 1.1, "{:.2f}".format(threshold),
            horizontalalignment="center",
            verticalalignment="bottom",
            fontweight="bold",
            fontsize=fontsize * 0.8,
            fontname=kwargs.get('fontfamily'),
            color="#aaaaaa",
            )
             
    if n_points == 0:
        return
    ax.text(
        0.95, 0.9, "<{:.2f} : n={:,}\n({:.0%})".format(threshold, n_pass, float(n_pass) / n_points),
        horizontalalignment="right",
        verticalalignment="top",
        fontsize=fontsize,
        color="#222222",
        fontweight="bold",
        fontname=kwargs.get('fontfamily'),
        transform=ax.transAxes,
        **ANNOTATION_KWARGS

        )
    pass


def add_annotations(ax, data, metric_label, col_id, row_id, **kwargs):
    ''' Depending on the metric being plotted,
    optionally add further annotations to the
    axis. For instance, a threshold line or
    text labels'''
    metric_label = metric_label.strip()
#     logger.info('Adding annotations')
    logger.info(metric_label)
    if metric_label.lower() == "reproducibility":
        return _add_annotation_reproducibility(ax, data, metric_label, col_id, row_id, **kwargs)
    else:
        logger.info("'{}', '{}'".format(metric_label, 'reproducibility'))

    if 'recall' in metric_label.lower():
        return _add_annotation_recall(ax, data, metric_label, col_id, row_id, **kwargs) 


def plot_row_of_histograms(
        df, gs, category_order,
        n_rows, n_cols,
        plot_columns, column_display_names, bins,
        row_label, row_sublabel,
        fontfamily, colors,
        xtick_orientation, ylabel_fontsize, xlabel_fontsize, xlabel_fontcolor, ylabel_fontcolor):
    name = df.name
    row_id = df[category_order].unique()
    assert len(row_id) == 1
    row_id = row_id[0]
    font = fontfamily
    fontweight = 600
    
    if type(bins) == int:
        bins = np.linspace(0, 1, bins)
        
    for j, (metric, colname) in enumerate(zip(plot_columns, column_display_names)):
        col_id = j
        counter = int(row_id * n_cols + col_id)
        ax = plt.subplot(gs[counter])

        with sns.axes_style('white'):
            try:
                data = df[metric].dropna()
                plt.hist(data, bins=bins, lw=1, edgecolor="#ffffff", color=str(colors[col_id]))

            except Exception as e:
                plt.text(0.01, 0.5, 'ERROR')
                logger.errot(str(e))
            
            if row_id == 0:
                plt.xlabel(colname + "  ",
                           rotation='horizontal',
                           fontweight=fontweight,
                           horizontalalignment="center",
                           fontname=font,
                           color=xlabel_fontcolor,
                           fontsize=xlabel_fontsize)
                plt.gca().xaxis.set_label_position('top') 
            if (col_id == 0):
                
                plt.text(-0.1, 0.3, row_sublabel,
                    horizontalalignment="right", fontsize=ylabel_fontsize * 0.8, color="#444444",
                        transform=ax.transAxes)
                plt.ylabel("{}  \n".format(row_label),
                           rotation='horizontal',
                           fontweight=fontweight,
                           verticalalignment="center",
                           horizontalalignment="right",
                           fontname=font,
                           color=ylabel_fontcolor,
                           fontsize=ylabel_fontsize)
                
            if row_id != n_rows - 1:
                plt.xticks([])
            else:
                if xtick_orientation == "vertical":
                    plt.xticks(rotation="vertical")
                
            plt.yticks([])
            
            annotation_kwargs = ANNOTATION_KWARGS.copy()
            annotation_kwargs.update(
                dict(fontfamily=font)
                )
            add_annotations(plt.gca(), data, colname, col_id, row_id, **annotation_kwargs)
            
                
def break_lines(s):
    '''Split a long phrase by putting the first word
    on the first line and everything else on the second
    line by inserting a newline between the two.'''
    x = s.split(" ")
    if len(x) == 1:
        return s
    return "{}\n{}".format(x[0], " ".join(x[1:]))
       

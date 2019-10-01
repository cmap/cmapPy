
'''
Created on Sep 30, 2019

@author: Navid Dianati
@contact: navid@broadinstitute.org
'''
import logging
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.gridspec as gridspec

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def stratogram(
    data,
    category,
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
    "category" variable. Each column of the grid is one metric, and each row
    depicts a stratum of the data.
    @param data: Pandas DataFrame where each row is a data point and the
    metrics and other variables are in the columns.
    @param category: string name of the column that defines the stratum/
    category of each data point.
    @param category_order: string name of the integer column that defines
    the order in which each stratum should be plotted in the rows. There
    should be a one-to-one map between the category and category_order
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
    assert category in df.columns
    assert category_order in df.columns

    logger.info('Validating the table')
    for metric in metrics:
        assert metric in df.columns, metric

    # Update category order to "remove" non-existent categories
    dict_new_order = {x:i for i, x in  enumerate(sorted(df[category_order].unique().tolist()))}
    df[category_order] = df[category_order].apply(lambda x:dict_new_order[x])
    n_rows = df[category_order].nunique()
    
    n_cols = len(metrics)
    plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(n_rows, n_cols)
    gs.update(wspace=0.0, hspace=0.0)
    
    # Group the data by the category variable and for each stratum
    # Plot a row of histograms in the grid.
    (
        df
        .groupby(category)
        .apply(
            plot_row_of_histograms,
            gs,
            category_order,
            n_rows,
            n_cols,
            plot_columns=metrics,
            column_display_names=column_display_names,
            bins=bins,
            fontfamily=fontfamily,
            colors=colors,
            xtick_orientation=xtick_orientation,
            ylabel_fontsize=ylabel_fontsize,
            xlabel_fontsize=xlabel_fontsize,
            xlabel_fontcolor=xlabel_fontcolor,
            ylabel_fontcolor=ylabel_fontcolor,
            )
    )
    
    if outfile:
        plt.savefig(outfile, bbox_inches='tight')


def plot_row_of_histograms(df, gs, category_order, n_rows, n_cols, plot_columns, column_display_names, bins,
                      fontfamily, colors,
                      xtick_orientation, ylabel_fontsize, xlabel_fontsize, xlabel_fontcolor, ylabel_fontcolor):
    name = df.name
    row_id = df[category_order].unique()
    assert len(row_id) == 1
    row_id = row_id[0]
    font = fontfamily
    fontweight = 600
    
    n_points = len(df)
    
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
                print str(e)
            
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
                plt.text(-0.1, 0.3, "(n={:,})".format(n_points),
                    horizontalalignment="right", fontsize=ylabel_fontsize * 0.8, color="#444444",
                        transform=ax.transAxes)
                plt.ylabel("{}  \n".format(name),
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
            
                
def break_lines(s):
    '''Split a long phrase by putting the first word
    on the first line and everything else on the second
    line by inserting a newline between the two.'''
    x = s.split(" ")
    if len(x) == 1:
        return s
    return "{}\n{}".format(x[0], " ".join(x[1:]))
       



import logging

from IPython.display import display

import numpy as np
import pandas as pd 

logger = logging.getLogger()


def cohort_view_table(df,
                      category_label="category_label",
                      category_order="category_order",
                      flags=[],
                      flag_display_labels=[],
                     add_percentages=True):

    ''' Generate a DataFrame showing counts and percentages
    of subsets (defined by flags), stratified by categories.
    For instance, each row (category) may be a selectivity
    bucket, and each column can be the number of compounds in
    that bucket that passed a given threshold. A "Total"
    column shows the total number of compounds in each 
    bucket and a grand total sums them all up.
    @param df: DataFrame where each row is a compound and
    columns are various metrics and flags
    @kwarg category_label: name of the column that defines
    a category. The data is stratified based on this fieild.
    @kwarg category_order: order in which the categories should
    be displayed as rows of the table. There should be a one
    to one correspondence between category_label and category_order.
    @kwarg flags: list of column names defining binary flags. 
    These flags define subsets that will be counted and displayed
    as columns of the output table.
    @kwarg flag_display_labels: string labels for output columns
    corresonding to flags
    @kwarg add_percentages: whether to display percentages 
    alongside the counts.
    '''
    assert len(flags) == len(flag_display_labels), '"flags" and "flag_display_labels" should have the same length'
    
    df['Total'] = 1
    columns = ['Total'] + flags 
    df = (
        df
        .groupby([category_order, category_label])[columns]
        .sum()
        .sort_index(axis=0, level=category_order)
        .reset_index(level=[category_order])
        .drop(columns=category_order)
    )

    column_names = ["Total"] + flag_display_labels 
    df.columns = column_names
    df.index.names = ['Category'] 

    df = df.T
    num_categories = len(df.columns)
    logger.info("num_categories: {}".format(num_categories))

    # Test comopound fields
    cpd_fields = [c for c in df.columns if 'Test subset' in c]
    if len(cpd_fields) != 0:
        df['Test Compounds Total'] = df[cpd_fields].sum(1)
    df['Grand Total'] = df.iloc[:, :num_categories].sum(1)
    df = df.T
    df.index.name = None
    
    if add_percentages:
        df = df.transform(_add_row_percentages, axis=1)
    return df


def _fmt_total_percentages(x, total):
    '''
    Formatting function for DataFrame.Style. Formats the 
    "Total" column to show percentages. 
    '''
    s = '''<span style="width:50%;float: left;text-align:right;font-weight:bold">{:,d} </span>
    <span style="font-size:1em;color:#FF7043;width:50%;text-align:left;float: right;padding-left:1em;font-weight:bold">
    ({:.0%})</span>'''.format(int(x), float(x) / total)
    return s


def _add_row_percentages(s):
    '''Convert all columns except for "Total" to a string
    that shows the integer count as well as the percentage
    of Total within the row.'''
    s = s + 0
    index = s.index
    assert "Total" in index
    total = s['Total']
    for label, x in s.iteritems():
        if label == "Total":
            continue
        s[label] = '''<span style="width:50%;float: left;text-align:right">{:,d} </span>
        <span style="font-size:1em;color:#888888;width:50%;text-align:left;float: right;padding-left:1em">
        ({:.0%})</span>'''.format(int(x), float(x) / total)
    return s


def display_cohort_stats_table(table, barplot_column):
    font_family = "Roboto"
    idx = pd.IndexSlice
    # indexes of the rows corresponding to categories, exludes 
    # the last "total" sums
    group_ids = [x for x in table.index if 'Total' not in x]
    
    barplot_max = table.loc[group_ids, barplot_column].sum()
    
    # Sum of numbers in Total column (excluding Grand Total, obviously)
    total = table.loc['Grand Total', 'Total']
    table_stylized = (
        table
        .style
        .format(
            lambda s: _fmt_total_percentages(s, total),
            subset=pd.IndexSlice[:, 'Total']
        )
        .applymap(lambda x : 'text-align:center;')
        .applymap(lambda x: "border-left:solid thin #d65f5f", subset=idx[:, barplot_column])
        .bar(subset=idx[group_ids, barplot_column], color='#FFDACF', vmin=0, vmax=barplot_max)
        .applymap(lambda x: "padding:0.5em 1em 0.5em 1em")
        .applymap(lambda x: "background:#444;color:white;border:solid thin #000;font-weight:bold", subset=idx['Grand Total', :])
        .applymap(lambda x: "border-left:solid thin #ddd", subset=idx[:, 'Total'])
         .set_table_styles(
             [
                 {'selector' : 'table',
                  'props' : [('font-family', font_family), ('font-size', '30px'), ('border', 'solid thin #999')]
                 },
                 {'selector' : 'thead, tbody', 'props' : [
                     ('border', 'solid 1px #ddd'),
                 ]
                 },
                 {'selector' :
                  'thead', 'props' : [
                     ('border-bottom', 'solid 2px #ddd'),
                     ('border-top', 'solid 2px #ddd'),
                     ('background', '#fefefe'), ('text-align', 'center'),
                     ('font-family', font_family),
                      ('font-size' , '1em')
                 ]
                 },
                 {'selector' : 'th',
                  'props' : [ 
                      ('text-align', 'center'),
                      ('color' , '#444'),
                  ]
                 },
                 {'selector' : 'th.col_heading',
                  'props' : [ 
                      ('max-width', '8em')
                  ]
                 },
                 {'selector' : 'th:not(.blank)',
                  'props' : [ 
#                       ('border-left','solid thin #ddd'), 
#                       ('border-right','solid thin #ddd'), 
                  ]
                 },
                 {'selector' : 'tbody', 'props' : [ 
                     ('text-align', 'center'), ('background', '#fff'), ('font-size' , '1.em'),
                                                   ('font-family', font_family)]},
                 {'selector' : '.row_heading',
                  'props' : [('border-right', 'solid thin #ddd'), ('text-align', 'left')]}                 
             ]
          )
        )
    if 'Test Compounds Total' in table.index:
        table_stylized = table_stylized.applymap(lambda x: "border-top:solid thin #aaa", subset=idx['Test Compounds Total', :])
    
    return table_stylized

'''
This script contains examples for reading .gctx files in Python.
'''

import cmap.io.gct as gct
import cmap.io.plategrp as grp

# give input file
path_to_gctx_file = '../data/modzs_n272x978.gctx'

# read the full data file
GCTObject = gct.GCT(path_to_gctx_file)
GCTObject.read()
print(GCTObject.matrix)

# read the first 100 rows and 10 columns of the data
GCTObject = gct.GCT(path_to_gctx_file)
GCTObject.read(row_inds=range(100),col_inds=range(10))
print(GCTObject.matrix)

# read the first 10 columns of the data, identified by their
# column ids, stored in a grp file given below
path_to_column_ids = '../data/cids_n10.grp'
# read the column ids as a list
column_ids = grp.read_grp(path_to_column_ids)
GCTObject = gct.GCT(path_to_gctx_file)
# extract only the specified columns from the matrix
GCTObject.read(cid=column_ids)
print(GCTObject.matrix)

# get the available meta data headers for data columns and row
column_headers = GCTObject.get_chd()
row_headers = GCTObject.get_rhd()

# get the perturbagen description meta data field from the column data
inames = GCTObject.get_column_meta('pert_iname')

# get the gene symbol meta data field from the row data
symbols = GCTObject.get_row_meta('pr_gene_symbol')

GCTObject.write('../data/python_example.gctx')

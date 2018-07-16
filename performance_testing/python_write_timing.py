# '/path/to/large/gctx/file' refers to a large GCTX file (any size above 10174x100000 should work) from which file subsets are made.
# In testing, the large GCTX file used lacked metadata; including metadata would cause slight variation in results.
# Cache was cleared in between consecutive operations.

import os
import time
import pandas as pd
import cmapPy.pandasGEXpress.write_gctx as write_gctx
import cmapPy.pandasGEXpress.write_gct as write_gct
import cmapPy.pandasGEXpress.parse as parse
import cmapPy.pandasGEXpress.subset_gctoo as sg

# for storing timing results
gct_times = {}
gctx_times = {}

# large input gctx; see notes above for more info about this
big_gctoo = parse.parse("/path/to/large/gctx/file")

# column and row spaces to test writing on
col_spaces = [96, 384, 1536, 3000, 6000, 12000, 24000, 48000, 100000]
row_spaces = [978, 10174]

for c in col_spaces:
	for r in row_spaces:
		curr_gctoo = sg.subset_gctoo(big_gctoo, ridx = range(0, r), cidx=range(0,c))
		# gct writing 
		out_fname = "write_test_n" + str(c) + "x" + str(r) + ".gct"
		start = time.clock()
		write_gct.write(curr_gctoo, out_fname)
		end = time.clock()
		elapsed_time = end - start
		gct_times[out_fname] = elapsed_time
		os.remove(out_fname)
		# gctx writing 
		out_fname = "write_test_n" + str(c) + "x" + str(r) + ".gctx"
		start = time.clock()
		write_gctx.write(curr_gctoo, out_fname)
		end = time.clock()
		elapsed_time = end - start
		gctx_times[out_fname] = elapsed_time
		os.remove(out_fname)

# write results to file
gct_df = pd.DataFrame(pd.Series(gct_times))
gctx_df = pd.DataFrame(pd.Series(gctx_times))
write_times_df = pd.concat([gct_df, gctx_df])
write_times_df.columns = ["write_time"]
write_times_df.to_csv("python_writing_results.txt", sep="\t")

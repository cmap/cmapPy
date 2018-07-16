# '/path/with/gctx/files/to/test/*gct*' refers to a directory of GCT and/or GCTX files to time parsing operations on.
# Cache was cleared in between consecutive operations. 

import time
import pandas as pd 
import glob
import cmapPy.pandasGEXpress.parse as parse

# for storing timing results
parse_times = {}

# input directory of files (gct or gctx) to test
input_files = glob.glob("/path/with/gctx/files/to/test/*gct*")

for f in input_files:
	start = time.clock()
	in_gctoo = parse.parse(f)
	end = time.clock()
	elapsed_time = end - start
	parse_times[f] = elapsed_time

# write results to file
parse_time_series = pd.Series(parse_times)
parse_time_series.to_csv("python_parsing_results.txt", sep="\t")




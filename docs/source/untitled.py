import pandas as pd 
import glob 

out_files = glob.glob("*.out")

def filter_timing_results(my_list):
	keep = []
	for i in range(0, len(my_list)):
		if "src" in lines[i]:
			keep.append(lines[i])
		elif "elapsed_parse_time" in lines[i]:
			keep.append(lines[i] + lines[i + 2])
		elif "write_elapsed" in lines[i]:
			keep.append(lines[i] + lines[i + 2])
	return keep

for of in out_files:

	print("reformating: " + of)

	# open file
	with open(of) as f:
		lines = f.readlines()

	# remove whitespace
	lines = [l.strip() for l in lines]

	# filter for the lines we want
	filtered_lines = filter_timing_results(lines)

	# reformat so file name is column 1, and parse/write data is cols 2, 3
	filtered_lines_sublists = [filtered_lines[i:i+3] for i in range(0, len(filtered_lines), 3)]

	# convert list of lists to DF
	out_df = pd.DataFrame(filtered_lines_sublists [1:], columns=filtered_lines_sublists [0])

	# write data frame out
	curr_out_name = str.split(of, ".")[0] + ".txt"
	out_df.to_csv(curr_out_name, sep = "\t")

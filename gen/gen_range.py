import numpy as np
import argparse, random, decimal, csv, math

# take command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--length", type=int, default=100000,
					help="length of the request stream")
parser.add_argument("-a", "--alpha", type=float, default=1.5,
					help="Zipfian alpha value (a > 1)")
parser.add_argument("-s", "--sigma", type=float, default=5,
					help="STDEV of normal distribution for range length")
parser.add_argument("-o", "--outfile", type=str,
					default="workload",
					help="name of the output file ([outfile].csv)")
args = parser.parse_args()

# check if provided args are correct
assert args.length >= 0
assert args.alpha > 1
assert args.sigma > 0

# assign global variables
MAXINT = 2**32 - 1
LENGTH = args.length

# generate a Zipfian distribution of keys with a given length
x = np.random.zipf(args.alpha, LENGTH)

# generate a normally distributed range length
y = np.ceil(np.abs(np.random.normal(0, args.sigma, LENGTH))).astype(int)

# loop through the keys and assign request data
out = []
for i, j in zip(x, y):
	# append the request
	out.append([i, i + j, "range", 0])

# print out stats
print("Generated test workload with:")
print(f"{LENGTH} requests")
print(f"{len(set(x))} unique start keys")
print(f"Average range length: {np.average(y)}")
print(f"Maximum range length: {np.max(y)}")
print(f"Saved to {args.outfile}.csv")

# write data to CSV file
with open(args.outfile + '.csv', mode='w') as csv_file:
	csv_writer = csv.writer(csv_file, delimiter=',')
	for request in out:
		csv_writer.writerow(request)
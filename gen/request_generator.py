import numpy as np
import argparse, random, decimal, csv, math

# take command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--length", type=int, default=100000,
					help="length of the request stream")
parser.add_argument("-a", "--alpha", type=float, default=1.5,
					help="Zipfian alpha value (a > 1)")
parser.add_argument("-g", "--gets", type=float, default=0.6,
					help="ratio of gets in the stream")
parser.add_argument("-r", "--rngq", type=float, default=0.1,
					help="ratio of range queries in the stream")
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
assert args.gets + args.rngq <= 1

# assign global variables
MAXINT = 2**32 - 1

# use decimal library to work out suitable integer range for
# request type distribution
d = decimal.Decimal(str(args.gets + args.rngq)).as_tuple()
mul = 10**(-d.exponent) * (1 + (d.digits[-1] % 2 != 0))

# set criteria for request type comparison with integer distribution
RANGE = mul * args.rngq
GET = mul * (args.rngq + args.gets)
PUT = (GET + mul) / 2

# generate a Zipfian distribution of keys with a given length
x = np.random.zipf(args.alpha, args.length)

# generate a normally distributed range length
y = np.ceil(np.abs(np.random.normal(0, args.sigma, args.length))).astype(int)

# loop through the keys and assign request data
out = []
values = {}
for i, j in zip(x, y):
	# assign a request type
	r = random.randint(0, mul)
	if (r < RANGE): request_type = "range"
	elif (r < GET): request_type = "get"
	elif (r < PUT): request_type = "put"
	else: request_type = "delete"

	# increment value for put requests
	value = 0
	if request_type == "put":
		if i in values: values[i] += 1
		else: values[i] = 1
		value = values[i]

	# append the request
	out.append([i,
				(i + j) * int(request_type=="range"),
				request_type,
				value])

# print out stats
print("Generated test workload with:")
print(f"{args.length} requests")
print(f"{len(set(x))} unique start keys")
# print(f"Average range length: {np.average(y)}") ### not correct
# print(f"Maximum range length: {np.max(y)}")
print(f"Saved to {args.outfile}.csv")

# write data to CSV file
with open(args.outfile + '.csv', mode='w') as csv_file:
	csv_writer = csv.writer(csv_file, delimiter=',')
	for request in out:
		csv_writer.writerow(request)
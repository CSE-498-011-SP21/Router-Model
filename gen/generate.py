import numpy as np
import argparse, random, decimal, csv

# take command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--length", type=int, default=100000,
					help="length of the request stream")
parser.add_argument("-s", "--skew", type=float, default=0.5,
					help="ratio of gets in the stream")
parser.add_argument("-o", "--outfile", type=str,
					default="workload",
					help="name of the workload save file")
args = parser.parse_args()

# check if provided args are correct
assert args.length >= 0
assert args.skew >= 0 and args.skew <= 1

# assign global variables
MAXINT = 2**32 - 1
LENGTH = args.length
GETS = args.skew

# use decimal library to work out suitable integer range for
# request type distribution
d = decimal.Decimal(str(GETS)).as_tuple()
mul = 10**(-d.exponent) * (1 + (d.digits[-1] % 2 != 0))

# generate a Zipfian distribution of keys with a given length
x = np.random.zipf(1.5, LENGTH)

# loop through the keys and assign request data
out = []
values = {}
for i in x:
	# assign a request type
	r = random.randint(0, mul)
	if (r < mul*GETS): request_type = "get"
	elif (r < mul*(GETS+1)/2): request_type = "put"
	else: request_type = "delete"

	# increment value for put requests
	value = 0
	if request_type == "put":
		if i in values: values[i] += 1
		else: values[i] = 1
		value = values[i]
	
	# append the request
	out.append([i, request_type, value])

# write data to CSV file
with open(args.outfile + '.csv', mode='w') as csv_file:
	csv_writer = csv.writer(csv_file, delimiter=',')
	for request in out:
		csv_writer.writerow(request)
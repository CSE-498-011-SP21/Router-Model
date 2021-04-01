import numpy as np
import csv, random

MAXINT = 2**32 - 1
LENGTH = 1000000

# generate a Zipfian distribution with a given length
x = np.random.zipf(1.5, LENGTH)

# assign random keys to the elements in the distribution
mapping = {}
y = []
for i in range(len(x)):
	if x[i] not in mapping:
		mapping[x[i]] = random.randint(0, MAXINT)
	y.append(mapping[x[i]])

# write key stream to CSV file
with open('stream.csv', mode='w') as csv_file:
	csv_writer = csv.writer(csv_file, delimiter=',')
	csv_writer.writerow(y)

# loop over the distribution and keep track of the most used keys
usage = {}
for key in y:
	if key in usage:
		usage[key] += 1
	else:
		usage[key] = 1

# write usage data to CSV file
with open('frequency.csv', mode='w') as csv_file:
	csv_writer = csv.writer(csv_file, delimiter=',')
	for key in usage:
		csv_writer.writerow([key, usage[key]])
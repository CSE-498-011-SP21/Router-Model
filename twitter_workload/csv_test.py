import csv

with open('cluster001') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	keys = []
	for row in csv_reader:
		keys.append(row[1])

print(f"Number of keys: {len(keys)}")
print(f"Number of unique keys: {len(set(keys))}")

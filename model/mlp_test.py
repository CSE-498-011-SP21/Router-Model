import numpy as np
import random
from sklearn.neural_network import MLPClassifier

MAXINT = 2**32 - 1
LENGTH = 100

# generate a Zipfian distribution with a given length
x = np.random.zipf(1.5, LENGTH)

# assign random keys to the elements in the distribution
mapping = {}
y = []
for i in range(len(x)):
	if x[i] not in mapping:
		mapping[x[i]] = random.randint(0, MAXINT)
	y.append(mapping[x[i]])

# loop over the distribution and keep track of the most used keys
usage = {}
for key in y:
	if key in usage:
		usage[key] += 1
	else:
		usage[key] = 1

# preallocate arrays
data = np.empty((len(usage), 1))
target = np.empty((len(usage,)), dtype=np.int)

for i, key in enumerate(usage):
	data[i] = np.asarray([key / MAXINT], dtype=np.float64)
	target[i] = np.asarray([int(usage[key] > 3)], dtype=np.int)
	i += 1

print(data)
print(target)


clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
                    hidden_layer_sizes=(20,20), random_state=0)

clf.fit(data, target)
print(clf.predict(data))

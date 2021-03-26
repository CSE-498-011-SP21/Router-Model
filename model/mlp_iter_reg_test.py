import numpy as np
import random
from sklearn.neural_network import MLPRegressor

MAXINT = 2**32 - 1
LENGTH = 10000

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

# # preallocate arrays
# data = np.empty((len(usage), 1))
# target = np.empty((len(usage,)), dtype=np.int)

# for i, key in enumerate(usage):
# 	data[i] = np.asarray([key / MAXINT], dtype=np.float64)
# 	target[i] = np.asarray([usage[key]], dtype=np.int)
# 	i += 1

# print(data)
# print(target)



# # convert array y to 2d and scale
# y = np.asarray(y).reshape(len(y), 1)

# preallocate data array
data = np.empty((len(y), 1))

for i, key in enumerate(y):
	data[i] = np.asarray([key / MAXINT], dtype=np.float64)




clf = MLPRegressor(hidden_layer_sizes=10, random_state=0, max_iter=10,
					batch_size=1)

clf.fit(data, np.ones(len(data)))

for i, result in enumerate(clf.predict(np.asarray(list(usage)).reshape(len(usage), 1))):
	print(f"{usage[list(usage)[i]]}: {result}")

# print(clf.predict(data))
# print(clf.score(data, target))

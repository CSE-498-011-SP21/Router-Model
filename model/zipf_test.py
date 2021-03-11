import numpy as np
import random

MAXINT = 2**32 - 1

x = np.random.zipf(1.5, 100)

mapping = {}
y = []
for i in range(len(x)):
	if x[i] not in mapping:
		mapping[x[i]] = random.randint(0, MAXINT)
	y.append(mapping[x[i]])

print(x)
print(y)
print(mapping)
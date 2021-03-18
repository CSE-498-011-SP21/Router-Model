import numpy as np
import random
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

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
	data[i] = np.asarray([key], dtype=np.int)
	target[i] = np.asarray([int(usage[key] > 4)], dtype=np.int)
	i += 1
# print(usage)
print(data)
print(target)

logreg_clf = LogisticRegression()
logreg_clf.fit(data, target)
print(logreg_clf.predict(data))

SVC_model = SVC()
SVC_model.fit(data, target)
print(SVC_model.predict(data))
import numpy as np
import random
from sklearn.neural_network import MLPRegressor

# Numeric Python Library.
import numpy
# Scikit-learn Machine Learning Python Library modules.
#   Preprocessing utilities.
from sklearn import preprocessing
# Python graphical library
from matplotlib import pyplot

# Keras perceptron neuron layer implementation.
from keras.layers import Dense
# Keras Dropout layer implementation.
from keras.layers import Dropout
# Keras Activation Function layer implementation.
from keras.layers import Activation
# Keras Model object.
from keras.models import Sequential


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

# preallocate arrays
data = np.empty((len(usage), 1))
target = np.empty((len(usage,)), dtype=np.int)

for i, key in enumerate(usage):
	data[i] = np.asarray([key / MAXINT], dtype=np.float64)
	target[i] = np.asarray([usage[key]], dtype=np.int)
	i += 1

#print(data)
#print(target)


# New sequential network structure.
model = Sequential()

# Input layer with dimension 1 and hidden layer i with 128 neurons. 
model.add(Dense(64, input_dim=1, activation='relu'))
# Dropout of 20% of the neurons and activation layer.
model.add(Dropout(.2))
model.add(Activation("linear"))
# Hidden layer j with 64 neurons plus activation layer.
model.add(Dense(32, activation='relu'))
model.add(Activation("linear"))
# Hidden layer k with 64 neurons.
model.add(Dense(32, activation='relu'))
# Output Layer.
model.add(Dense(1))

# Model is derived and compiled using mean square error as loss
# function, accuracy as metric and gradient descent optimizer.
model.compile(loss='mse', optimizer='adam', metrics=["accuracy"])

# Training model with train data. Fixed random seed:
numpy.random.seed(3)
model.fit(data, target, nb_epoch=256, batch_size=1, verbose=2)

for i, result in enumerate(model.predict(data)):
	print(f"{target[i]}: {result}")

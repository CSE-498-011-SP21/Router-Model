# For this part, set a reward that when send the key to cpu, it will be reward 1,the gpu will be reward to 0 or -1. So we try to calculate all key's frequency and choosing the biggest k keys to sent to cpu.
# we will send the data set y from client to the model to init it. Then we send the k to label the dataset y, and return the data after nomorlizing to [0,1] and target label.
class RL_label:
    def __init__(self, y):
      self.y = y
      self.usage = {}
      self.fre = []
    
    def bound(self, k):
      for key in y:
	      if key in self.usage:
		      self.usage[key] += 1
	      else:
		      self.usage[key] = 1
      for i, key in enumerate(self.usage):
        self.fre.append(self.usage[key])
      data = np.empty((len(self.usage), 1))
      target = np.empty((len(self.usage,)), dtype=np.int)
      self.fre.sort()
      bound = self.fre[len(self.fre)-k]

      for i, key in enumerate(self.usage):
        data[i] = np.asarray([key], dtype=np.int)/(1.0e+10)
        if self.usage[key] > bound :
	        target[i] = 1
	        i += 1
        else :
          target[i] = -1
          i += 1
      return data, target



from sklearn import svm
#Increase the penalty of svc to improve its accuracy, but the generalization ability becomes weaker, and svc is suitable for training below 10000 data, and linearsvc is suitable for training above 10000
#SVM is good for two class classification
clf = svm.SVC(C=10000000.0)
clf.fit(data, target)
print(clf.predict(data))


lin_clf = svm.LinearSVC(C=10000000.0)
lin_clf.fit(data, target)
print(lin_clf.predict(data))

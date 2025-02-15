# nn_backprop_YL.py
# Python 3.x

import numpy as np
import random
import math
import sys

# helper functions

def loadFile(df):
  # load a comma-delimited text file into an np matrix
  resultList = []
  f = open(df, 'r')
  for line in f:
    line = line.rstrip('\n')  # "1.0,2.0,3.0"
    sVals = line.split(',')   # ["1.0", "2.0, "3.0"]
    fVals = list(map(np.float32, sVals))  # [1.0, 2.0, 3.0]
    resultList.append(fVals)  # [[1.0, 2.0, 3.0] , [4.0, 5.0, 6.0]]
  f.close()
  return np.asarray(resultList, dtype=np.float32)  # not necessary
# end loadFile
  
	
class NeuralNetwork:

  def __init__(self, numInput, numHidden, numOutput, seed):
    self.ni = numInput
    self.nh = numHidden
    self.no = numOutput
	
    self.iNodes = np.zeros(shape=[self.ni], dtype=np.float32)
    self.hNodes = np.zeros(shape=[self.nh], dtype=np.float32)
    self.oNodes = np.zeros(shape=[self.no], dtype=np.float32)
	
    self.ihWeights = np.zeros(shape=[self.ni,self.nh], dtype=np.float32)
    self.hoWeights = np.zeros(shape=[self.nh,self.no], dtype=np.float32)
	
    self.hBiases = np.zeros(shape=[self.nh], dtype=np.float32)
    self.oBiases = np.zeros(shape=[self.no], dtype=np.float32)
	
    self.rnd = random.Random(seed) # allows multiple instances
    self.initializeWeights()
 	
  def setWeights(self, weights):
    if len(weights) != self.totalWeights(self.ni, self.nh, self.no):
      print("Warning: len(weights) error in setWeights()")	

    idx = 0
    for i in range(self.ni):
      for j in range(self.nh):
        self.ihWeights[i,j] = weights[idx]
        idx += 1
		
    for j in range(self.nh):
      self.hBiases[j] = weights[idx]
      idx += 1

    for j in range(self.nh):
      for k in range(self.no):
        self.hoWeights[j,k] = weights[idx]
        idx += 1
	  
    for k in range(self.no):
      self.oBiases[k] = weights[idx]
      idx += 1
	  
  def getWeights(self):
    tw = self.totalWeights(self.ni, self.nh, self.no)
    result = np.zeros(shape=[tw], dtype=np.float32)
    idx = 0  # points into result
    
    for i in range(self.ni):
      for j in range(self.nh):
        result[idx] = self.ihWeights[i,j]
        idx += 1
		
    for j in range(self.nh):
      result[idx] = self.hBiases[j]
      idx += 1

    for j in range(self.nh):
      for k in range(self.no):
        result[idx] = self.hoWeights[j,k]
        idx += 1
	  
    for k in range(self.no):
      result[idx] = self.oBiases[k]
      idx += 1
	  
    return result
 	
  def initializeWeights(self):
    numWts = self.totalWeights(self.ni, self.nh, self.no)
    wts = np.zeros(shape=[numWts], dtype=np.float32)
    lo = -0.01; hi = 0.01
    for idx in range(len(wts)):
      wts[idx] = (hi - lo) * self.rnd.random() + lo
    self.setWeights(wts)

  def computeOutputs(self, xValues):
    hSums = np.zeros(shape=[self.nh], dtype=np.float32)
    oSums = np.zeros(shape=[self.no], dtype=np.float32)

    self.iNodes = xValues
      
    hSums = np.matmul(np.transpose(self.ihWeights),self.iNodes)
    hSums = np.add(hSums,self.hBiases)
    
    # tanh activation function for each hj
    for j in range(self.nh):
      self.hNodes[j] = self.hypertan(hSums[j])
     
    oSums = np.matmul(np.transpose(self.hoWeights),self.hNodes)      
    oSums = np.add(oSums,self.oBiases)
 
    softOut = self.softmax(oSums)
    self.oNodes = softOut
	  
    result = self.oNodes  
    return result
	
  def train(self, trainData, maxEpochs, learnRate):
    hoGrads = np.zeros(shape=[self.nh, self.no], dtype=np.float32)  # hidden-to-output weights gradients
    obGrads = np.zeros(shape=[self.no], dtype=np.float32)  # output node biases gradients
    ihGrads = np.zeros(shape=[self.ni, self.nh], dtype=np.float32)  # input-to-hidden weights gradients
    hbGrads = np.zeros(shape=[self.nh], dtype=np.float32)  # hidden biases gradients
	
    delta_k = np.zeros(shape=[self.no], dtype=np.float32)  # output signals: dEn/d(ak)     
    delta_j = np.zeros(shape=[self.nh], dtype=np.float32)  # hidden signals: dEn/d(aj)

    epoch = 0
    x_values = np.zeros(shape=[self.ni], dtype=np.float32)
    t_values = np.zeros(shape=[self.no], dtype=np.float32)
    numTrainItems = len(trainData)
    indices = np.arange(numTrainItems)  # [0, 1, 2, . . n-1]  # rnd.shuffle(v)

    while epoch < maxEpochs:
      self.rnd.shuffle(indices)  # scramble order of training items
      for ii in range(numTrainItems):
        idx = indices[ii]
        
        x_values = trainData[idx,0:self.ni] # get the input values	
        t_values = trainData[idx,self.ni:self.ni+self.no] # get the target values       
        self.computeOutputs(x_values)  # forward pass: results stored internally
		
        # backward pass:
        # 1. compute output node signals: delta_k
        for k in range(self.no):       
            delta_k[k] = self.oNodes[k] - t_values[k] # cross-entropy error function + softmax activation

        # 2. compute hidden-to-output weight gradients using output signals delta_k
        for j in range(self.nh):
          for k in range(self.no):
            hoGrads[j, k] = delta_k[k] * self.hNodes[j]
			
        # 3. compute output node bias gradients using output signals
        for k in range(self.no):
          obGrads[k] = delta_k[k] * 1.0  # 1.0 dummy input can be dropped
		  
        # 4. compute hidden node signals: delta_j
        for j in range(self.nh):         
          sum = np.matmul(self.hoWeights[j,:],delta_k)          
          derivative = (1 - self.hNodes[j]) * (1 + self.hNodes[j])  # h'(aj) for tanh activation
          delta_j[j] = derivative * sum
		 
        # 5 compute input-to-hidden weight gradients using hidden signals
        for i in range(self.ni):
          for j in range(self.nh):
            ihGrads[i, j] = delta_j[j] * self.iNodes[i]

        # 6. compute hidden node bias gradients using hidden signals
        for j in range(self.nh):
          hbGrads[j] = delta_j[j] * 1.0  # 1.0 dummy input can be dropped

        # update weights and biases using the gradients
		
        # 1. update input-to-hidden weights
        for i in range(self.ni):
          for j in range(self.nh):
            dE = -1.0 * learnRate * ihGrads[i,j]
            self.ihWeights[i, j] += dE
			
        # 2. update hidden node biases
        for j in range(self.nh):
          dE = -1.0 * learnRate * hbGrads[j]
          self.hBiases[j] += dE      
		  
        # 3. update hidden-to-output weights
        for j in range(self.nh):
          for k in range(self.no):
            dE = -1.0 * learnRate * hoGrads[j,k]
            self.hoWeights[j, k] += dE
			
        # 4. update output node biases
        for k in range(self.no):
          dE = -1.0 * learnRate * obGrads[k]
          self.oBiases[k] += dE
 		  
      epoch += 1
	  
      if epoch % 10 == 0: # print training mse every 10 epochs
        mse = self.meanSquaredError(trainData)
        print("epoch = " + str(epoch) + " ms error = %0.4f " % mse)
    # end while
    
    result = self.getWeights()
    return result # return the trained weights
  # end train
  
  def accuracy(self, tdata):  # train or test data matrix, calculate classificaiton accuracy rate
    num_correct = 0; num_wrong = 0
    x_values = np.zeros(shape=[self.ni], dtype=np.float32)
    t_values = np.zeros(shape=[self.no], dtype=np.float32)

    for i in range(len(tdata)):  # walk thru each data item
      for j in range(self.ni):  # peel off input values from curr data row 
        x_values[j] = tdata[i,j]
      for j in range(self.no):  # peel off tareget values from curr data row
        t_values[j] = tdata[i, j+self.ni]

      y_values = self.computeOutputs(x_values)  # computed output values)
      max_index = np.argmax(y_values)  # index of largest output value 

      if abs(t_values[max_index] - 1.0) < 1.0e-5:
        num_correct += 1
      else:
        num_wrong += 1

    return (num_correct * 1.0) / (num_correct + num_wrong)

  def meanSquaredError(self, tdata):  # on train or test data matrix, mse between the network output and the target values
    sumSquaredError = 0.0
    x_values = np.zeros(shape=[self.ni], dtype=np.float32)
    t_values = np.zeros(shape=[self.no], dtype=np.float32)

    for ii in range(len(tdata)):  # walk thru each data item
      for jj in range(self.ni):  # peel off input values from curr data row 
        x_values[jj] = tdata[ii, jj]
      for jj in range(self.no):  # peel off tareget values from curr data row
        t_values[jj] = tdata[ii, jj+self.ni]

      y_values = self.computeOutputs(x_values)  # computed output values
	  
      for j in range(self.no):
        err = t_values[j] - y_values[j]
        sumSquaredError += err * err  # (t-o)^2
		
    return sumSquaredError / len(tdata)
          
  @staticmethod
  def hypertan(x):
    if x < -20.0:
      return -1.0
    elif x > 20.0:
      return 1.0
    else:
      return math.tanh(x)

  @staticmethod	  
  def softmax(oSums):
    result = np.zeros(shape=[len(oSums)], dtype=np.float32)
    m = max(oSums)
    divisor = 0.0
    for k in range(len(oSums)):
       divisor += math.exp(oSums[k] - m)
    for k in range(len(result)):
      result[k] =  math.exp(oSums[k] - m) / divisor
    return result
	
  @staticmethod
  def totalWeights(nInput, nHidden, nOutput):
   tw = (nInput * nHidden) + (nHidden * nOutput) + nHidden + nOutput
   return tw

# end class NeuralNetwork

def main():
  
  numInput = 4
  numHidden = 5
  numOutput = 3
  print("\nCreating a %d-%d-%d neural network " %
    (numInput, numHidden, numOutput) )
  nn = NeuralNetwork(numInput, numHidden, numOutput, seed=3)
  
  print("\nLoading Iris training and test data ")
  trainDataPath = "irisTrainData.txt"
  trainDataMatrix = loadFile(trainDataPath)
#  print("\nTest data: ")
#  showMatrixPartial(trainDataMatrix, 4, 1, True)
  testDataPath = "irisTestData.txt"
  testDataMatrix = loadFile(testDataPath)
  
  maxEpochs = 200
  learnRate = 0.005
  print("\nSetting maxEpochs = " + str(maxEpochs))
  print("Setting learning rate = %0.3f " % learnRate)
  print("\nStarting training")
  nn.train(trainDataMatrix, maxEpochs, learnRate)
  print("Training complete")
  
  accTrain = nn.accuracy(trainDataMatrix)
  accTest = nn.accuracy(testDataMatrix)
  
  print("\nAccuracy on 120-item train data = %0.4f " % accTrain)
  print("Accuracy on 30-item test data   = %0.4f " % accTest)
  
  print("\nEnd demo \n")
   
if __name__ == "__main__":
  main()

# end script


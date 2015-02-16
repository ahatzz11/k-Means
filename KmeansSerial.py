import numpy
import random
import timeit

def distance(x,y):
    sumOfSquares =0
    for column in range(0,len(x)):
        sumOfSquares = sumOfSquares + (x[column] - y[column])**2
    return sumOfSquares

filename = 'twoCircles.txt'

k=3             #Number of clusters. 
maxIterations = 20 #maximum number of iterations.
epsilonThreshold =0.00001
    
data = numpy.loadtxt(filename)
means = numpy.zeros((k,data.shape[1])) #This is for holding the means..
membership = numpy.zeros(len(data)) #This is for the clustering assignment
delta = 1 #to pass the initial test..
iterations = 0

    #Choose k random points as the initial means..
initialMeans = random.sample(list(data),k)
start = timeit.default_timer()
while iterations < maxIterations and delta > epsilonThreshold: #Keep iterating as long 
    rowIndex = 0
    for row in data:
        index = 1
        clusterIndex = 1
        minDistance = numpy.sum((row - initialMeans[0])**2)
        for i in range(1,k):
            prevDistance = numpy.sum((row - initialMeans[i])**2)
            index = index + 1
            if(prevDistance < minDistance):
                minDistance = prevDistance
                clusterIndex = index

        membership[rowIndex] = clusterIndex
        rowIndex = rowIndex + 1
        #Find New Means
    for i in range(0,k):
        ids = numpy.where(membership == i + 1)
        myPoints = data[ids,]
        if len(ids[0]) == 1:
           means[i,:] = myPoints
        else:
            means[i,:] = numpy.mean(myPoints, axis = 1)
    delta = 0
    for row in range(0,k):
        delta = delta + distance(means[row], initialMeans[row])
    initialMeans = means
    print(delta)
    iterations = iterations + 1
    #calculate Delta, difference between the old means and the new means..

print('Time')
print(timeit.default_timer() - start)
print('Means')
print(means)
print('Membership')
print(membership)

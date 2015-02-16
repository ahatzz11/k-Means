# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 10:57:00 2014

@author: Sean Luthjohn
Alex Hatzenbuhler
Chris Barnick
"""

import random
#import pylab
import threading
import timeit
#import numpy

#Public variables that are used throughout the code
lock = threading.Semaphore(1)#lock used to lock the accessing of the cluster counts array
membership = [] #Will contain a points memberhsip. The cluster a point is part of.
k = 2 #Number of clusters
clusterCounts = [0] * k #The number of points each cluster will contain
d = 0 #The number of columns
n = 0 #The number of rows
clusterSums = [[0 for i in range(d)] for j in range(k)]
localCount = [0] *k #Will be assigned the cluster counts of each thread. Will be added to total cluster counts

'''
Method for clustering:
Looks for the nearest cluster and assigns the point to that cluster
The sum of squares is used as a distance measure to determine closeness to the centroids
'''
def clustering(startIndex, endIndex, initialMeans, k, n, data):
    localCount = [0] *k
    for row in range(startIndex, endIndex):
        rows = data[row]
        index = 1
        clusterIndex = 1
        minDistance = distance(rows, initialMeans[0])
        for i in range(1,k):
            prevDistance = distance(rows, initialMeans[i])
            index = index + 1
            if prevDistance < minDistance:
                minDistance = prevDistance
                clusterIndex = index

        membership[row] = clusterIndex
        localCount[clusterIndex-1] = localCount[clusterIndex-1] + 1

    for count in range(k):
        lock.acquire()
        clusterCounts[count] = clusterCounts[count] + localCount[count]
        lock.release()

'''
Method to find the sums for each of the clusters columns of data
The sums will be used alongside the counts to find the means of the clusters
Every thread passes there start and end index to this thread. That information is used to determine which points are to
be used.
localSums is each threads individual cluster sums. The localSums will be added to the clusterSums.
clusterSums is surrounded by a lock so only on thread can access it at time.
'''
def sums(local_start,local_end,data):
    localSums = [[0 for i in range(d)] for j in range(k)]
    for jj in range(local_start,local_end):
        clusterIndex = membership[jj]
        for ii in range(d):
            localSums[clusterIndex - 1][ii] = localSums[clusterIndex - 1][ii] + data[jj][ii]


    for cluster in range(k):
        for value in range(d):
            lock.acquire()
            clusterSums[cluster][value] = clusterSums[cluster][value] + localSums[cluster][value]
            lock.release()


'''
The distance function
Returns the sum of squares value.
Used to determine the distance between a point and a centroid and also used to determine the difference in the means
(initalMeans and newMeans)
'''
def distance(x, y):
    sumOfSquares = 0
    for column in range(0, d):
        sumOfSquares = sumOfSquares + (x[column] - y[column])** 2
    return sumOfSquares

'''
The main function
Used to create all threads and print results.
Reads data from a file and stores it into a 2d array
Calculation of means are performed here as well
'''
if __name__ == "__main__":
    delta = 1  #to pass the initial test..
    iterations = 0 #counter for the number of iterations
    filename = 'twoCircles.txt' #the file that is being used.
    k = 2  #Number of clusters.
    maxIterations = 20  #maximum number of iterations.

    #file is opened for reading
    f = open(filename, 'r')

    #loop through file to determine how many rows and columns there are
    for line in f:
        numbers = line.split()
        d = len(numbers)
        n = n + 1

    #data will store information in the file that was opened
    data = [[0 for i in range(d)] for j in range(n)]
    #inital means will store the initial centroids
    initialMeans = [[0 for i in range(d)] for j in range(k)]
    f.close() #file closed
    i = 0
    j = 0
    #file is opened again now for reading
    f = open(filename, 'r')
    #for every row in the file add it to the 2d array data
    for line in f:
        numbers = line.split()#split the line into an array
        j = 0
        #for each value in the array numbers add it to data
        for x in numbers:
            data[i][j] = float(x) #value x assigned to data at row i column j

            #The initial means are now retrieved
            if i == n/2:
                initialMeans[0][j] = float(x)
            elif i == n/8:
                initialMeans[1][j] = float(x)

            j = j + 1

        i = i + 1

    #Timer begins
    start = timeit.default_timer()
    #Continue performing kMeans until iterations is not less than maxIterations
    while iterations < maxIterations:
        clusterSums = [[0 for i in range(d)] for j in range(k)] #cluster sums reset for every iteration
        means = [[0 for i in range(d)] for j in range(k)] #means reset for every iteration
        localCount = [0] *k #reset for each iteration. Each threads cluster counts
        clusterCounts = [0] * k #reset for each iteration. The size of each cluster
        membership = [0 for i in range(n)] # reset for each iteration. Holds points membership to a cluster
        threads = [] #array to hold the created threads
        threadsAmount = 16 #variable for the number of threads that will be used
        '''
        Thread creation performed here
        Each thread gets its own start and end index and performs clustering
        '''
        for t in range(0, threadsAmount):
            local_n = int(n / threadsAmount)
            local_start = int(t * local_n)
            local_end = int(local_start + local_n)
            #print(local_n)
            #print(local_start)
            if t >= threadsAmount - 1:
                remainder = n % threadsAmount
                local_end = local_end + remainder
            #print(local_end)
            t = threading.Thread(target=clustering,args=(local_start,local_end,initialMeans,k,n,data))
            tt = threading.Thread(target=sums,args=(local_start,local_end,data))
            threads.append(t)
            t.start()

        '''
        Joining of threads
        Forces wait until all threads have completed clustering
        '''
        for t in threads:
            t.join()

        '''
        Thread creation performed
        Each thread gets its own start and end index
        Each thread performs sums and adds its local cluster sums to the total cluster sums
        clusterSums will be used to get the means
        '''
        for t in range(0, threadsAmount):

            local_n = int(n / threadsAmount)
            local_start = int(t * local_n)
            local_end = int(local_start + local_n)
            #print(local_n)
            #print(local_start)
            if t >= threadsAmount - 1:
                remainder = n % threadsAmount
                local_end = local_end + remainder
            #print(local_end)
            t = threading.Thread(target=sums,args=(local_start,local_end,data))
            threads.append(t)
            t.start()

        '''
        Joining of threads
        Forces wait until all threads have completed sums
        '''
        for t in threads:
            t.join()

        #delta value
        delta = 0

        #Means for each cluster are calculated
        #The cluster sums and counts are used
        for i in range(0, k):
            for ii in range(0, d):
                means[i][ii] = clusterSums[i][ii] / clusterCounts[i]

        #delta value is determined
        for xx in range(0, k):
            delta = delta + distance(means[xx], initialMeans[xx])

        #if the delta is equal to 0 or the means haven't changed then exit loop
        if delta == 0 or (initialMeans == means):
            break
        #print('delta')
        #print(delta)

        #reassign means
        intialMeans = means

        #increment iterations
        iterations = iterations + 1

    #Print of execution time in seconds
    stop = timeit.default_timer()

    print('Membership')
    print(membership)
    print('Means')
    print(means)
    print('cluster counts')
    print(clusterCounts)
    print('Time in Seconds')
    print(stop - start)



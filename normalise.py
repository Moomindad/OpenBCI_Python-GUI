# Takes an array of arrays of vectors, and first makes a single array of vectors from it.
# Example for testing[<3>,<3>,<5>]
#

import numpy as np


class Normaliser(object):

    def __init__(self, brain_data=[]):

        if brain_data==[]:
            self.brain_data = np.load("TestData2017-10-21_12-58-18.npy")
        else:
            self.brain_data = brain_data

        self.np_minmax(self.brain_data)



    def flatten(self, arr):
        s2 = []
        for item in arr:
            s2.extend(item)
        return s2


    def minmaxVector(self, arr):
        vectorlen = len(arr[0])
        max = arr[0]
        min = [0] * vectorlen

        s1 = len(arr) - 1
        s2 = vectorlen

        for row in range(s1):
            for col in range(s2):
                if arr[row][col] < min[col]:
                    min[col] = arr[row][col]
                if arr[row][col] > max[col]:
                    max[col] = arr[row][col]

        print(max)
        print(min)

        return min, max

    def remove_linebreaks(self, line):
        # First we remove the line breaks...
        #
        fline = line[:-1]

        return fline


    def normfactor(self, listMin, listMax):
        normlist = [0] * (len(listMin) - 1)
        baselist = [0] * (len(listMin) - 1)
        for item in range(len(listMin) - 1):
            baselist[item] = listMax[item] - listMin[item]
            normlist[item] = listMax[item] + baselist[item]

        return baselist, normlist

    #============================================================================
    # Takes an array with 2D-arrays and gets the chanmin and chanmax-values of the two. It returns
    # three values, an chanmin-value vector, a chanmax-value vector, and a baseline vector (containing
    # the normalisation factor).
    #
    def np_minmax(self, arr1):

        # First we try to find the minimum and maximum values of all the channels.
        #
        chanmin1 = np.amin(np.amin(arr1, axis=0), axis=0)
        chanmax1 = np.amax(np.amax(arr1, axis=0), axis=0)

        self.sign = np.sign(chanmax1)

        self.inverted_sign = self.sign * -1

        self.basevalues = (chanmax1 - chanmin1)  * self.inverted_sign

        self.chanmin = chanmax1  * self.sign
        self.chanmax = chanmin1  * self.sign

        return self.chanmin, self.chanmax, self.basevalues


    def preprocess(self, brainD):
        for i in range(np.alen(brainD)):
            brainD[i] = self.one_chunk(brainD[i])
        return brainD

    def one_chunk(self, chunk):
        return (chunk[0] * self.sign - self.basevalues) / self.basevalues

### SANDBOX AREA
#
#
fo = np.load("2017-10-27_12-33-7.csvnpy.npy")

print(fo)


norm = Normaliser(fo)

print(norm.preprocess(norm.brain_data))


"""


# print(fo)

a = list(fo)

b = flatten(a)

normA, normB = minmaxVector(b)

print(normA)
print(normB)


print(normfactor(normA,normB))



"""

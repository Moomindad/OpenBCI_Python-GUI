
class MinMaxModule:


    def __init__(self, file):

        self.filename = file

        self.no_Channels = 8

        self.minVector = [0,0,0,0,0,0,0,0]
        self.maxVector = [0,0,0,0,0,0,0,0]
        self.collectorVector = []

        self.fileobject = open(self.filename, mode='r')


    def readAFile(self):

        while True:
            oneline = self.fileobject.readline().split(',')[:9][:-1]
            if (oneline == [''] or oneline == []):
                return 1

            for i in range(0,8):
                oneline[i] = int(oneline[i])

            self.collectorVector += [oneline]
            # print(self.collectorVector.__len__())


    def getMax(self):
        for item in self.collectorVector:
            for i in range(0, 8):
                if item[i] > self.maxVector[i]:
                    self.maxVector[i] = item[i]

    def getMin(self):

        # We need to make a copy of the array, otherwise the values will be updated in
        # both arrays in parallel
        #
        self.minVector = self.maxVector.copy()
        for item in self.collectorVector:
            for i in range(0, 8):
                if item[i] < self.minVector[i]:
                    self.minVector[i] = item[i]




a = MinMaxModule("31-10-2017 20:2:7positions.txt")
a.readAFile()
a.getMax()
a.getMin()

print(a.minVector)
print(a.maxVector)







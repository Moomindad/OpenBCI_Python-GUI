
class SampleReader (object):

    def __init__(self, filename="sampledata.csv"):

       self.file = open(filename,"r")

    def next(self):

        temp = self.file.readline()

        if temp == '':
            return ''
        else:
            temp = temp.split(',')

            temp = [int(x) for x in temp]

            return temp

        return ''


    def exit(self):
        self.file.close()

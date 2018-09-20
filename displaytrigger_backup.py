#!/usr/bin/env python3.6

#
# Imports for the GUI handling
#
# All global values are declared in the config file.
#
import config as cfg

# noinspection PyCompatibility
from tkinter import *
from PIL import ImageTk, Image

from random import randint


import threading
import os

from dictionary import Dictionary as dict

TIME = [
    5,
    10,
    15,
    20
]

IMAGES = [
    'Colours',
    'Basic shapes',
    'Images'
]


class DisplayTrigger(object):

    NEUTRAL = -1

    def __init__(self):

        # ========================
        # Create window instance
        #
        self.win = Toplevel()
        self.win.title(dict.get_string('shapes'))
        self.win.minsize(width=1000, height=500)
        self.pane = Canvas(self.win, width=1000, height=500, borderwidth="4")
        self.pane.pack()

        self.neutralImagedir = 'Images/Neutral/'
        self.imageDirectory = 'Images/Fruits/'

        self.images = self.selfiles(3)

        self.win.update()

        self.neutral = False
        self.counter = 1
        self.displaythread = self.ticker()

        self.triggerValue = DisplayTrigger.NEUTRAL

        self.win.update()



    def ticker(self):
        return threading.Timer(2.0, self.tickit)

    def tickit(self):
        # We display a neutral image between the triggers.
        #
        if self.neutral:
            self.displayImage(self.neutralImagedir + "0.jpg")
            self.neutral = False
            self.triggerValue = DisplayTrigger.NEUTRAL
        else:
            selected = randint(0,self.images.__len__() - 1)
            self.displayImage(self.imageDirectory + self.images[selected])
            self.neutral = True
            self.triggerValue = selected

        print(self.counter)
        print(self.triggerValue)
        self.counter += 1

    def displayImage(self, filepath):
        if os.path.exists(filepath):
            print(filepath)
            self.im = ImageTk.PhotoImage(Image.open(filepath))
            self.pane.create_image((500, 250), image=self.im)
            self.pane.update()
        else:
            print(filepath + " does not exit")

    # Returns a list with a given number of image files in
    # the current image directory.
    #
    def selfiles(self, number_of):
        temp = os.listdir(self.imageDirectory)
        result = list()
        for i in range(number_of):
            selected = randint(0,temp.__len__() - 1)
            t1 = temp[selected:selected + 1]
            result += t1
            temp = temp[:selected] + temp[selected+1:]

        return result

    def connect(self):
        return self.triggerValue

# a = Displaytrigger()
# a.displaythread.start()


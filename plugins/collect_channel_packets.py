#!/usr/bin/env python3.6
"""
This plugin collects data for deep learning purposes. It utilises a value flag to store the output variable (y_value)
and saves the polled data in a large nympy array (+ writing it to a text file.


"""
# IMPORTS
#
import datetime
import timeit
from dictionary import Dictionary as dict

import numpy as np

from tkinter import *
from tkinter import ttk

import threading

import plugin_interface as plugintypes

import userGUI as main_window

import displaytrigger as trig

class PluginChanCollect(plugintypes.IPluginExtended):

    __main_instance__ = None

    def __init__(self, file_name="chanpackets", delim=",", verbose=True):

        # The y_value is used to store the current flag_value for the output categories in keras.
        #
        self.y_value = 0

        __main_instance__ = self

        now = datetime.datetime.now()

        self.format = "NP"

        self.panel = main_window.UserGUI.__pluginSpace__

        self.time_stamp = '%d-%d-%d_%d-%d-%d' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        self.file_name = self.time_stamp
        self.start_time = timeit.default_timer()
        self.delim = delim
        self.verbose = False
        self.first_row = True

        # This is for collecting the data from the openBCI session in string form.
        #
        self.data_arr = ""

        # Collecting real variables as well.
        #
        self.data_arr_np = []
        self.arr_collector = []

        self.start_time = timeit.default_timer()
        self.t2 = 0.0
        self.break_time = 0.3

        self.pack_size = 30
        self.no_of_packets = 0

    def activate(self):

        self.trigger = trig.Displaytrigger()

        if len(self.args) > 0:
            if 'no_time' in self.args:
                self.file_name = self.args[0]
            else:
                self.file_name = self.args[0] + '_' + self.file_name
            if 'verbose' in self.args:
                self.verbose = True

        self.file_name = self.file_name + '.csv'

        print("Will export data to:" + self.file_name + ".npy/csv")

        # self.data_arr_np = np.array([])

        self.data_arr = '['

        # Create separate control window.
        #
        win_thread = threading.Thread(target=self.open_control_window)
        win_thread.start()

        self.trigval = self.trigger.connect()
        self.trigger.displaythread.start()

        # Open the file in append mode
        #
        with open(self.file_name + ".csv", 'a') as f:
            f.write('%' + self.time_stamp + '\n')

    # The deactivate function is used to close down the plugin in a controlled way.
    #
    def deactivate(self):

        # close the last array, even though it might not be complete...
        #
        # Adjust the last delimiting commas, and add proper array ends.
        #
        self.data_arr = self.data_arr[:-2] + ']]\n'

        #
        # write last array, and then close the file. If written in TEXT format, the result is a string. Otherwise
        # it is saved in numpy format.
        #
        with open(self.file_name + ".csv", 'a') as f:
            f.write(self.data_arr)
            f.close()

        np.save(self.file_name + "npy", np.asarray(self.arr_collector))

        print(dict.get_string('plugclose') + self.file_name)
        print(dict.get_string('checkarray'))

        return

    def show_help(self):
        print("Optional argument: [filename] (default: collect.csv)")


    def __call__(self,sample):

        t = timeit.default_timer() - self.start_time

        # print(timeSinceStart|Sample Id)
        #
        # For every first row in the array, we will perform some initialisations.
        #
        if self.first_row:
            self.t2 = t

            # Initialise each subarray with the proper delimiters
            #
            self.data_arr += '['
            self.data_arr_np = []

            self.first_row = False

        # Each row is constructed separately. ========================
        #
        row = '['
        int_row = [ ]

        if self.verbose:
            row += str(t)
            row += self.delim
            row += str(sample.id)
            row += self.delim

        for i in sample.channel_data:
            int_row.append(abs(i))          # TODO check the polarity.
            row += str(abs(i))              # TODO likewise
            row += self.delim

        print("Row:")
        print(int_row)

        if self.verbose:
            row += "CSV: %f | %d" % (t, sample.id)

        row += '],\n'
        #
        # END of row =========================

        # Update packets per batch counter.
        #
        self.no_of_packets += 1

        self.data_arr += row

        self.data_arr_np.append(int_row)

        # Check if we have passed a chunk, depending on the set time limit.
        #
        deltat = t - self.t2

        # If the number of chunks in the packet is big enough, we pack it into a subarray.
        #
        if self.no_of_packets > self.pack_size:

            # TODO check this when running.
            #
            self.arr_collector.append(self.data_arr_np.append(self.trigval))

            print("Lump: ")
            print(self.data_arr_np)

            self.data_arr = self.data_arr[:-2] + ', ' + str(self.trigval) + '],\n'

            self.first_row = True

            with open(self.file_name, 'a') as f:
                f.write(self.data_arr)

            self.bLabel['text'] = str(deltat)

            self.no_packets = 0

    # def second__call__(self, sample):
    #     t = timeit.default_timer() - self.start_time
    #
    #     # print(timeSinceStart|Sample Id)
    #     #
    #     # For every first row in the array, we will perform some initialisations.
    #     #
    #     if self.first_row:
    #         if self.verbose:
    #             print("CSV: %f | %d" % (t, sample.id))
    #
    #         self.no_of_packets = 0
    #
    #         # Check the time that we start the first row.
    #         #
    #         self.t2 = t
    #
    #         # Initialise each subarray with the proper delimiters
    #         #
    #         self.data_arr += '['
    #         self.first_row = False
    #
    #     # Each row is constructed separately. ========================
    #     #
    #     row = '['
    #
    #     if self.verbose:
    #         row += str(t)
    #         row += self.delim
    #         row += str(sample.id)
    #         row += self.delim
    #
    #     for i in sample.channel_data:
    #         row += str(i)
    #         row += self.delim
    #
    #     if self.verbose:
    #         row += "CSV: %f | %d" % (t, sample.id)
    #
    #     row += '],\n'
    #     #
    #     # END of row =========================
    #
    #     # Update packets per batch counter.
    #     #
    #     self.no_of_packets += 1
    #
    #     self.data_arr += row
    #
    #     # Check if we have passed a chunk, depending on the set time limit.
    #     #
    #     deltat = t - self.t2
    #     print(deltat)
    #
    #     if self.no_of_packets > self.pack_size:
    #         self.data_arr = self.data_arr[:-2] +'],\n'
    #         self.first_row = True
    #
    #         with open(self.file_name, 'a') as f:
    #             f.write(self.data_arr)
    #
    #         self.bLabel['text'] = str(deltat)

    #
    # TODO check if this needs to specifically threaded.
    #


    def open_control_window(self):

        # ========================
        # Create Information space in the main window.
        #
        self.aLabel = ttk.Label(self.panel, text=dict.get_string('packtime'))
        self.aLabel.grid(column=0, row=0, sticky="WE")

        self.bLabel = ttk.Label(self.panel, text=str(self.break_time * 1000))
        self.bLabel.grid(column=1, row=0, sticky="WE")

        self.cLabel = ttk.Label(self.panel, text=dict.get_string('packets'))
        self.cLabel.grid(column=0, row=1, sticky="WE")

        self.dLabel = ttk.Label(self.panel, text=str(self.pack_size))
        self.dLabel.grid(column=1, row=1, sticky="WE")

        # self.win.mainloop()

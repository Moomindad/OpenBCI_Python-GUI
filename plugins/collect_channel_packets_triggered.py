#!/usr/bin/env python3.6
"""
This plugin collects data for deep learning purposes. It utilises a value flag to store the
output variable (y_value) and saves the polled data in a large nympy array (+ writing it to
a text file.

The data is collected in a way that makes it possible to use triggers, such as images, colours,
etc. The data is collected with timed packets, so as to distinguish intervalsa in connection
with the presentation of teh visual stimuli.

The trigger mechanism is available in the file displaytrigger.py

"""
# IMPORTS
#
import datetime
import threading
import timeit
from tkinter import ttk

import numpy as np

import config as cfg
import displaytrigger as trig
import plugin_interface as plugintypes
from dictionary import Dictionary as dict


class PluginChanCollectTrig(plugintypes.IPluginExtended):
    __main_instance__ = None

    def __init__(self, file_name="chanpackets", delimiter=",", verbose=True):

        # Registering this instance in the config file.
        #
        cfg.plugin_instance = self


        # The y_value is used to store the current flag_value for the output categories in keras.
        #
        self.y_value = 0

        # Semaphors
        #
        self.activated = False
        self.verbose = False
        #
        # The first row in each package has to be initiated in a special way.
        #
        self.first_row = True

        # This variable is declared as a place holder, which will be instantiated to the studyGUI
        # object when activated.
        #
        self.trigger = None

        # The trigger_value variable keeps track of which of the phases we are in.
        # Always start with the trigger_value set to black = 0
        #
        self.trigger_value = 0

        # Set current time at the initialisation
        #
        now = datetime.datetime.now()

        self.format = "NP"

        self.panel = cfg.pluginSpace

        # Initialise all the data about this session.
        #
        self.time_stamp = '%d-%d-%d_%d-%d-%d' % (now.year, now.month, now.day, now.hour, now.minute, now.second)

        # We use two separate files to store the numeric data (the sensor data) and the result (the trigger values).
        #
        self.data_file_name = file_name + "-data-" + self.time_stamp + ".csv"
        self.result_file_name = file_name + "-result-" + self.time_stamp + ".csv"

        # We also store it as numpy arrays.
        #
        self.data_file_name_np = file_name + "-data-" + self.time_stamp
        self.result_file_name_np = file_name + "-result-" + self.time_stamp

        # Store the starting time for the session
        #
        self.start_time = timeit.default_timer()
        self.delimiter = delimiter

        # This is for collecting the data from the openBCI session in string form.
        #
        self.data_arr_string = ''
        self.result_arr_string = ''

        # Collecting real data variables as well.
        #
        self.data_arr_np = np.array([], int)
        self.result_arr_np = np.array([], int)

        # We use a temporary variable to collect the packages
        #
        self.arr_collector = np.array([], int)

        self.t2 = 0.0

        self.break_time = 0.3

        # The packet size is normally set to 16, since we are using 16 channels (Cyton + Daisy). Should we use just 8
        # channels, (the Cyton board only) we need to set this number to 8 as well. The packets should be of the
        # size x * x in order for certain neural network methods to work.
        #
        self.pack_size = cfg.sensornumber - 1

        # We need to have a img_counter for the number of packets we have collected in the current sequence
        #
        self.no_of_packets = 0
        self.total_number_of_packets = 0

    # ==================================================
    # This is called when the plugin is activated.
    #
    def activate(self):

        # Create the studyGUI object here. If done in init() it will create three parallell instances.
        #
        self.trigger = trig.StudyGui()

        # To avoid multiple activations causing multiple windows and menus.
        #
        if not self.activated:

            self.activated = True

            if len(self.args) > 0:
                if 'no_time' in self.args:
                    self.data_file_name = self.args[0]
                else:
                    self.data_file_name = self.args[0] + '_' + self.data_file_name
                if 'verbose' in self.args:
                    self.verbose = True

            # self.data_file_name = self.data_file_name + '.csv'

            print("Will export data to:" + self.data_file_name)

            # Create separate control window, in a separate thread.
            #
            win_thread = threading.Thread(target=self.open_control_window)
            win_thread.start()

            # self.trigger.studyStart()

            # Open the file in append mode
            #
            with open(self.data_file_name, 'a') as f:
                f.write('%' + self.time_stamp + '\n')

    # The deactivate function is used to close down the plugin in a controlled way.
    #
    def deactivate(self):

        # close the last array, even though it might not be complete...
        #
        # Adjust the last delimiting commas, and add proper array ends.
        #
        self.data_arr_string = self.data_arr_string[:-2] + ']]\n'

        #
        # write last array, and then close the file. If written in TEXT format, the result is a string. Otherwise
        # it is saved in numpy format.
        #
        with open(self.data_file_name, 'a') as f:
            f.write(self.data_arr_string)
            f.close()

        with open(self.result_file_name, 'a') as f:
            f.write(self.result_arr_string)
            f.close()

        np.save(self.data_file_name_np, self.data_arr_np)
        np.save(self.result_file_name_np, self.result_arr_np)

        print(dict.get_string('plugclose') + self.data_file_name)
        print(dict.get_string('checkarray'))

        return

    def show_help(self):
        print("Optional argument: [filename] (default: collect.csv)")

    # ======================================================
    # ======================================================
    # This is called from the openBCI-streamer. This part has to be as fast as possible.
    #
    def __call__(self, sample):

        # if sample.channel_data == '':
        #     self.deactivate()
        #     exit()

        # TODO this has to be implemented properly.
        #
        # if not cfg.study_running:  # If we do not run the study, we just return from the call.
        #     return
        #
        # If no image is shown (i.e.) black background, then we have set the trigger value to 0 (which equals the
        # background data type).
        #
        if not cfg.image_shown:
            self.trigger_value = 0

        # If we start with a new image, the trigger value is reset to one, and then the new_image flag is reset to False
        #
        if cfg.new_image:
            self.trigger_value = 1
            cfg.new_image = False

        # Calculate the time passed since start. This is for adding the delta time if needed.
        #
        self.t = timeit.default_timer() - self.start_time

        # =========================================================================
        # FIRST ROW
        # print(timeSinceStart|Sample Id)
        # =========================================================================
        # For every first row in the array, we will perform some initialisations.
        #
        if self.first_row:
            self.t2 = self.t

            # Initialise each subarray with the proper delimiters
            #
            self.data_arr_string = '['  # First row has an extra '[' added to contain the pack. Level 2

            # self.data_arr_np = np.array([])

            self.first_row = False

        # Each row is then constructed separately and added to the resulting array.
        # ========================================================================
        # Since we use extra information about the row, we put it into an extra
        # list level for the string version.
        #
        # [ 1
        #   [2 [3 [4 datalist]4,
        #      [datalist],...]3,
        #      [resultlist] ]2,
        #
        #   [2 [[datalist],
        #       [datalist],...],
        #      [resultlist]],
        # ]1
        #

        # =========================================================================
        # EVERY ROW
        # =========================================================================
        #
        row = '['   # Level 4

        # =========================================================================
        # COLLECTING SAMPLE DATA
        # =========================================================================
        # Checking the data and adding it into rows, both numeric and string-form in parallell.
        #
        # First the int data in a numpy array.
        #
        self.int_row_np = np.array(sample.channel_data)  # TODO check the polarity. Is abs() necessary?

        for i in sample.channel_data:
            row += str(abs(i))          # TODO likewise
            row += self.delimiter       # Default delimiter is ','

        row = row[:-1] + '],\n'     # Level 4. The slicing is necessary to take away a superfluous ','
                                    # before the last ']'
        #
        # =========================================================================
        # END OF ROW COLLECTION
        # =========================================================================
        #
        # Update packets per batch img_counter.
        #
        self.no_of_packets += 1

        # Add the string version of the row.
        #
        self.data_arr_string += row

        # Add the np component to the collector array.
        #
        if np.size(self.arr_collector) == 0:
            self.arr_collector = np.hstack((self.arr_collector, self.int_row_np))
        else:
            self.arr_collector = np.vstack((self.arr_collector, self.int_row_np))

        delta_t = self.t - self.t2

        # =========================================================================
        # EACH CHUNK
        # print(timeSinceStart|Sample Id)
        # =========================================================================
        # Check if we have passed a chunk, depending on the set time limit.
        #
        # If the number of chunks in the packet is big enough, we pack the current string
        # into a subarray.
        #
        # The size is determined by the number of electrodes used on the board (normally 16)
        #
        if self.no_of_packets > self.pack_size:

            self.total_number_of_packets = self.total_number_of_packets +1
            print(self.total_number_of_packets)


            # TODO check this when running
            #
            # Append the current chunk to the array, and then append the trigger
            # value to the result.
            #
            # First the numpy data
            #
            if np.size(self.data_arr_np) == 0:
                self.data_arr_np = np.array(self.arr_collector)
            else:
                self.data_arr_np = np.vstack((self.data_arr_np, self.arr_collector))

            self.result_arr_np = np.hstack((self.result_arr_np, np.array(self.trigger_value)))

            # Then the string data
            #
            self.data_arr_string = self.data_arr_string[:-2] + '],\n'

            # Write the package content in string form to the file.
            #
            with open(self.data_file_name, 'a') as f:
                f.write(self.data_arr_string)

            # Write the corresponding trigger value to the result file
            #
            with open(self.result_file_name, 'a') as f:
                f.write(cfg.triggervalstr[self.trigger_value] + '\n')

            # Level 3 and 2
            #
            # We just separate the eight first samples in each bunch into separate patterns
            #
            if self.trigger_value < 8:
                self.trigger_value += 1

            # If we start on a new package, we need to have a new first row.
            #
            self.first_row = True

            self.bLabel['text'] = str(delta_t)

            self.no_of_packets = 0

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
    #         self.data_arr_string += '['
    #         self.first_row = False
    #
    #     # Each row is constructed separately. ========================
    #     #
    #     row = '['
    #
    #     if self.verbose:
    #         row += str(t)
    #         row += self.delimiter
    #         row += str(sample.id)
    #         row += self.delimiter
    #
    #     for i in sample.channel_data:
    #         row += str(i)
    #         row += self.delimiter
    #
    #     if self.verbose:
    #         row += "CSV: %f | %d" % (t, sample.id)
    #
    #     row += '],\n'
    #     #
    #     # END of row =========================
    #
    #     # Update packets per batch img_counter.
    #     #
    #     self.no_of_packets += 1
    #
    #     self.data_arr_string += row
    #
    #     # Check if we have passed a chunk, depending on the set time limit.
    #     #
    #     deltat = t - self.t2
    #     print(deltat)
    #
    #     if self.no_of_packets > self.pack_size:
    #         self.data_arr_string = self.data_arr_string[:-2] +'],\n'
    #         self.first_row = True
    #
    #         with open(self.data_file_name, 'a') as f:
    #             f.write(self.data_arr_string)
    #
    #         self.bLabel['text'] = str(deltat)

    #
    # TODO check if this needs to specifically threaded.
    #

    #


    def open_control_window(self):

        # ========================
        # Create Information space in the main window.
        #
        self.aLabel = ttk.Label(self.panel, text=dict.get_string('packno'))
        self.aLabel.grid(column=0, row=0, sticky="WE")

        self.bLabel = ttk.Label(self.panel, text=str(self.total_number_of_packets))
        self.bLabel.grid(column=1, row=0, sticky="WE")

        self.cLabel = ttk.Label(self.panel, text=dict.get_string('packets'))
        self.cLabel.grid(column=0, row=1, sticky="WE")

        self.dLabel = ttk.Label(self.panel, text=str(self.pack_size + 1))
        self.dLabel.grid(column=1, row=1, sticky="WE")

# END OF FILE
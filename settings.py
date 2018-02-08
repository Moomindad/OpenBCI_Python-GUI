#!/usr/bin/env python3.6
#
# This is a communication class between the GUI and the controller. Ideally all the data should be
# shared through this object.
#
import pickle


class BCIsettings(object):

    def __init__(self):
        self.fileName = "settings.bci"  # =======================

        # Default settings.
        #
        self.boardType = "Cyton"

        # Since not all run with daisyboards, we put the default to no daisyboard.
        #
        self.daisyBoard = False

        # 16 channels is more than enough. All Cyton active to start with. Daisy board channels are issued as
        # non-active by default.
        #
        self.channels = [1, 1, 1, 1, 1, 1, 1, 1]
        self.dchannels = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.portUsed = None
        self.filteringEnabled = True
        self.logging = False
        self.baudrate = 115200

        # Impedance and auxiliaries are not used currently.
        #
        self.impedance = False

        self.aux = False,

        self.timeout = 100

        self.scaling = 0

        self.plugins = [['print']]

    # =======================
    # Setters and getters
    #
    # Do not access the settings content directly through the variables,
    # please use the setters and getters below.
    #
    # =======================
    # Using the daisyboard or not (Boolean)
    #
    def set_daisy(self, value):
        self.daisyBoard = value
        return self.daisyBoard

    def get_daisy(self):
        return self.daisyBoard

    # The type of board used.
    #
    def set_board_type(self, value):
        self.boardType = value
        return self.boardType

    def get_board_type(self):
        return self.boardType

    # The proper port to use.
    #
    def set_port(self, port):
        self.portUsed = port

    def get_port(self):
        return self.portUsed

    # Logging enabled or disabled. (Boolean)
    #
    def set_logging(self, booleanvalue):
        self.logging = booleanvalue

    def get_logging(self):
        return self.logging

    def get_baudrate(self):
        return self.baudrate

    def set_baudrate(self, rate=115200):
        self.baudrate = rate

    def set_timeout(self, val):
        self.timeout = val

    def get_timeout(self):
        return self.timeout

    def set_scaling(self, value):
        self.scaling = value

    def get_scaling(self):
        return self.scaling

    def set_channels(self, chans):
        self.channels = chans

    def get_channels(self):
        return self.channels

    def set_dchannels(self, chans):
        self.dchannels = chans

    def get_dchannels(self):
        return self.dchannels

    def get_plugins(self):
        return self.plugins

    def set_plugins(self, plugins):
        self.plugins = plugins

        print("Stored plugins:")
        print(self.get_plugins())

    # ===========================================================
    # We need to be able to save the settings.
    #
    def save_settings(self):
        with open(self.fileName, 'wb') as output:
            pickle.dump(output, -1)


    # Restoring the settings is a different matter.
    #
    def restore_settings(self):
        with open(self.fileName, 'rb') as f:
            return pickle.load(f)

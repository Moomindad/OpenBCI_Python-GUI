#!/usr/bin/env python3.6

"""
Core OpenBCI object for handling connections and samples from the board.

This represents the model in the program, i.e., all that has to do with the board control and
workings.

EXAMPLE USE:

    def handle_sample(sample):
        print(sample.channel_data)

    board = OpenBCIBoard()
    board.print_register_settings()
    board.start_streaming(handle_sample)

The callback (in this case the handle_sample function) is normally one or more of the plugins.

NOTE: If daisy modules is enabled, the callback will occur every two samples, hence "packet_id" will only contain
even numbers. As a side effect, the sampling rate will be divided by 2.

FIXME: at the moment we can just force daisy mode, do not check that the module is detected.

TODO: enable impedance

"""
# ===================
# Imports
# ===================
#
import atexit
import glob
import logging
import struct
import sys
import threading
import time
import timeit

import config as cfg

import numpy as np
import serial

import sample_reader as sr

# Importing two static objects.
#
from dictionary import Dictionary as dict

# ========================
# Constant values
#
SAMPLE_RATE = 250.0  # Hz
START_BYTE = 0xA0  # start of data packet
END_BYTE = 0xC0  # end of data packet
ADS1299_Vref = 4.5  # reference voltage for ADC in ADS1299.  set by its hardware
ADS1299_gain = 24.0  # assumed gain setting for ADS1299.  set by its Arduino code
scale_fac_uVolts_per_count = ADS1299_Vref / float((pow(2, 23) - 1)) / ADS1299_gain * 1000000.
scale_fac_accel_G_per_count = 0.002 / (pow(2, 4))  # assume set to +/4G, so 2 mG

'''
# Commands for in SDK http://docs.openbci.com/software/01-Open BCI_SDK:

command_stop = "s"
command_startText = "x"
command_startBinary = "b"
command_startBinary_wAux = "n"
command_startBinary_4chan = "v"
command_activateFilters = "F"
command_deactivateFilters = "g"
command_deactivate_channel = {"1", "2", "3", "4", "5", "6", "7", "8"}
command_activate_channel = {"q", "w", "e", "r", "t", "y", "u", "i"}
command_activate_leadoffP_channel = {"!", "@", "#", "$", "%", "^", "&", "*"}     //shift + 1-8
command_deactivate_leadoffP_channel = {"Q", "W", "E", "R", "T", "Y", "U", "I"}   //letters (plus shift) right below 1-8
command_activate_leadoffN_channel = {"A", "S", "D", "F", "G", "H", "J", "K"}     //letters (plus shift) below the 
                                                                                  //letters below 1-8
command_deactivate_leadoffN_channel = {"Z", "X", "C", "V", "B", "N", "M", "<"}   //letters (plus shift) below the 
                                                                                  // letters below the letters below 1-8
command_biasAuto = "`"
command_biasFixed = "~"
'''


class OpenBCIBoard(object):
    """

     Handle a connection to an OpenBCI board.

    Args:

      port: The port to connect to.
      baud: The baud of the serial connection.
      filter_data: ?
      scaled_output: ?
      daisy: Enable or disable daisy module and 16 channels readings
      aux, impedance: unused, for compatibility with ganglion API
      log: ?
      timeout: ?

    """

    def __init__(self,
                 ctr,
                 win
                 # The following values are now provided through the static settings object. This object
                 # can be saved and restored.
                 #
                 # See settings.py
                 #
                 # port=None,
                 # baud=115200,
                 # filter_data=True,
                 # scaled_output=True,
                 # daisy=False,
                 # aux=False,
                 # impedance=False,
                 # log=True,
                 # timeout=None
                 ):

        # Sometimes we need to request data from the user. Most of this communication, however,
        # should be done through the settings object. The most important use is to log messages
        # to the message box.
        #
        self.gui = win

        # Also we need to know about the controllers activities sometimes.
        #
        self.ctrl = ctr

        # The settings are shared between the GUI, the controller and the model. It is created and initialised in the
        # GUI (userGUI.py).
        #
        # self.settings = sets

        # Starting by finding the port, if it is not given by the GUI
        #
        if not cfg.portUsed:
            portUsed = self.find_port()

        # ========================
        # might be handy to know API
        #
        print(dict.get_string('v3connect') % cfg.portUsed)

        self.ser = serial.Serial(port=cfg.portUsed,
                                 baudrate= cfg.baudrate,
                                 timeout=cfg.timeout)

        win.log_mess(dict.get_string('estserial'))

        time.sleep(2)

        # Initialize 32-bit board, doesn't affect 8bit board
        #
        self.ser.write(b'v')

        # wait for device to be ready
        #
        time.sleep(1)

        self.print_incoming_text()

        # Initially the streaming of data is disabled.
        #
        self.streaming = False

        # Setting all default values.
        #
        self.eeg_channels_per_sample = 8  # number of EEG channels per sample *from the board*
        self.aux_channels_per_sample = 3  # number of AUX channels per sample *from the board*
        self.imp_channels_per_sample = 0  # impedance check not supported at the moment
        self.read_state = 0
        self.last_odd_sample = OpenBCISample(-1, [], [])  # used for daisy
        self.log_packet_count = 0
        self.attempt_reconnect = False
        self.last_reconnect = 0
        self.reconnect_freq = 5
        self.packets_dropped = 0

        # Disconnects from board when terminated
        #
        atexit.register(self.disconnect)

        self.gui.log_mess("Current board is: " + self.get_board_type())

        # When the board has been initialised, control is returned to the user, and nothing
        # happens until the user issues a command. This is mostly done through the GUI or menus.
        #

    # The methods available are listed here below.

    def get_board_type(self):
        """
        Returns the version of the board
        """
        return cfg.boardType

    def set_impedance(self, flag):
        """ Enable/disable impedance measure. Not implemented at the moment on Cyton. """
        return

    def ser_write(self, b):
        """Access serial port object for write"""
        self.ser.write(b)

    def ser_read(self):
        """Access serial port object for read"""
        return self.ser.read()

    def ser_in_waiting(self):
        """Access serial port object for inWaiting"""
        return self.ser.inWaiting()

    def get_sample_rate(self):
        if cfg.daisyBoard:
            return SAMPLE_RATE / 2
        else:
            return SAMPLE_RATE

    def get_nb_eeg_channels(self):
        if cfg.daisyBoard:
            return self.eeg_channels_per_sample * 2
        else:
            return self.eeg_channels_per_sample

    def get_nb_aux_channels(self):
        return self.aux_channels_per_sample

    def get_nb_imp_channels(self):
        return self.imp_channels_per_sample

    # This is for simple testing.
    #
    def handle_sample(sample):
        print(sample.channel_data)

    def start_streaming_thread(self,callbacks):
        streamthread = threading.Thread(target=self.start_streaming, args=(callbacks, ))
        streamthread.start()

    def start_streaming(self, callback, lapse=-1):


        """
        Start handling streaming data from the board. Call a provided callback
        for every single sample that is processed (every two samples with daisy module).

        Args:
          callback: A callback function -- or a list of functions -- that will receive a
          single argument of the OpenBCISample object captured.

          The valid callback functions are the plugins listed in the plugin directory.

          lapse: TODO: needs to be described
        """
        if not self.streaming:
            self.ser.write(b'b')
            self.streaming = True
            print("Streaming started")

        start_time = timeit.default_timer()

        # Enclose callback function in a list if it comes alone
        #
        if not isinstance(callback, list):
            callback = [callback]

        # Initialize check connection
        #
        self.check_connection()

        """ 
        This while-loop in the class has not been touched between v3 and v4 apart 
        from correcting pure errors.
        """

        # reader = sr.SampleReader()

        while self.streaming:

            # read current sample
            #
            # TODO RESTORE THIS AFTER TESTING

            # sample = OpenBCISample(-1, reader.next(), [])

            sample = self._read_serial_binary()

            #
            # If a daisy module is attached, wait to concatenate two samples (main board + daisy)
            # before passing it to callback
            #
            if cfg.daisyBoard:
                #
                # Odd sample: daisy sample, save for later (tilde is the invert operator)
                #
                if ~ sample.id % 2:
                    self.last_odd_sample = sample
                #
                # Even sample: concatenate and send if last sample was the first part, otherwise drop
                # the packet
                #
                elif sample.id - 1 == self.last_odd_sample.id:
                    #
                    # The aux data will be the average between the two samples, as the channel
                    # samples themselves have been averaged by the board
                    #
                    avg_aux_data = list((np.array(sample.aux_data) + np.array(self.last_odd_sample.aux_data)) / 2)
                    whole_sample = OpenBCISample(sample.id, sample.channel_data + self.last_odd_sample.channel_data,
                                                 avg_aux_data)
                    for call in callback:
                        call(whole_sample)
            else:
                for call in callback:
                    call(sample)

            if lapse > 0 and timeit.default_timer() - start_time > lapse:
                self.stop()
            if cfg.logging:
                self.log_packet_count = self.log_packet_count + 1

    """
      PARSER:
      Parses incoming data packet into OpenBCISample.
      Incoming Packet Structure:
      Start Byte(1)|Sample ID(1)|Channel Data(24)|Aux Data(6)|End Byte(1)
      0xA0|0-255|8, 3-byte signed ints|3 2-byte signed ints|0xC0 
    """

    # The binary signal stream is read into the memory.
    #
    def _read_serial_binary(self, max_bytes_to_skip=3000):

        # The local read function tests for a stalled stream. If not, the read bytes are returned.
        #
        def read(n):
            bb = self.ser.read(n)
            if not bb:
                self.warn(dict.get_string('stallwarn'))
                sys.exit()
                raise Exception(dict.get_string('stalled'))
                sys.exit()
                return '\xFF'
            else:
                return bb

        # if the stream is filled with trash, we can skip until the set limits of bytes until the start byte is
        # detected.
        #
        for rep in range(max_bytes_to_skip):

            #
            #  ---------Start Byte & ID---------
            #
            # We have to find the start byte in the stream, before we start reading.
            #
            if self.read_state == 0:

                # read 1 byte to start with
                #
                b = read(1)

                if struct.unpack('B', b)[0] == START_BYTE:

                    # Warn for skipped bytes in the beginning.
                    #
                    if rep != 0:
                        self.warn('Skipped %d bytes before start found' % (rep))
                        rep = 0

                    packet_id = struct.unpack('B', read(1))[0]  # packet id goes from 0-255
                    log_bytes_in = str(packet_id)

                    self.read_state = 1

            # If we have found the start byte and accepted it, we continue reading the data.
            #
            # ---------Channel Data---------
            #
            elif self.read_state == 1:

                channel_data = []

                # We have to read the whole number of used channels.
                #
                for c in range(self.eeg_channels_per_sample):

                    # The channel data is represented by 3 byte ints
                    #
                    literal_read = read(3)

                    unpacked = struct.unpack('3B', literal_read)
                    log_bytes_in = log_bytes_in + '|' + str(literal_read)

                    #
                    # Store the 3-byte int in 2s compliment
                    #
                    if unpacked[0] > 127:
                        pre_fix = bytes(bytearray.fromhex('FF'))
                    else:
                        pre_fix = bytes(bytearray.fromhex('00'))

                    literal_read = pre_fix + literal_read

                    # unpack little endian(>) signed integer(i) (makes unpacking platform independent)
                    #
                    myInt = struct.unpack('>i', literal_read)[0]

                    # finally we apply a proper scaling (if desired).
                    #
                    if cfg.scaling:
                        channel_data.append(myInt * scale_fac_uVolts_per_count)
                    else:
                        channel_data.append(myInt)

                self.read_state = 2

            #
            # ---------Accelerometer Data---------
            #
            elif self.read_state == 2:
                aux_data = []
                for a in range(self.aux_channels_per_sample):

                    # short = h
                    acc = struct.unpack('>h', read(2))[0]
                    log_bytes_in = log_bytes_in + '|' + str(acc)

                    if cfg.scaling:
                        aux_data.append(acc * scale_fac_accel_G_per_count)
                    else:
                        aux_data.append(acc)

                self.read_state = 3
            # ---------End Byte---------
            elif self.read_state == 3:
                val = struct.unpack('B', read(1))[0]
                log_bytes_in = log_bytes_in + '|' + str(val)
                self.read_state = 0  # read next packet
                if val == END_BYTE:
                    sample = OpenBCISample(packet_id, channel_data, aux_data)
                    self.packets_dropped = 0
                    return sample
                else:
                    self.warn("{0},{1} and {2}".format(packet_id, val, END_BYTE))
                    logging.debug(log_bytes_in)
                    self.packets_dropped = self.packets_dropped + 1

    """
  
    Clean Up (atexit)
  
    """

    def stop(self):

        print("Stopping streaming...\nWait for buffer to flush...")
        self.streaming = False
        self.ser.write(b's')
        self.ctrl.clean_up()
        if cfg.logging:
            logging.warning('sent <s>: stopped streaming')

    def disconnect(self):
        if (self.streaming == True):
            self.stop()
        if (self.ser.isOpen()):
            print("Closing Serial...")
            self.ser.close()
            logging.warning('serial closed')

    """
  
        SETTINGS AND HELPERS
  
    """

    # Method used to set the warning system started.
    #
    def warn(self, text):
        if cfg.logging:
            #
            # log how many packets where sent succesfully in between warnings
            #
            if self.log_packet_count:
                logging.info('Data packets received:' + str(self.log_packet_count))
                self.log_packet_count = 0
            logging.warning(text)



    def print_incoming_text(self):
        """

        When starting the connection, print all the debug data until
        we get to a line with the end sequence '$$$'.

        """
        line = ''
        # Wait for device to send data
        time.sleep(1)

        if self.ser.inWaiting():
            line = ''
            c = ''

            #
            # Look for end sequence $$$
            #
            while '$$$' not in line:
                c = self.ser.read().decode('utf-8',
                                           errors='replace')  # we're supposed to get UTF8 text,
                # but the board might behave otherwise
                line += c
            print(line)
        else:
            self.warn("No Message")

    def openbci_id(self, serial):
        """

        When automatically detecting port, parse the serial return for the "OpenBCI" ID.

        """
        line = ''

        #
        # Wait for device to send data
        #
        # time.sleep(2)

        if serial.inWaiting():
            line = ''
            c = ''
            # Look for end sequence $$$
            while '$$$' not in line:
                c = serial.read().decode('utf-8',
                                         errors='replace')  # we're supposed to get UTF8 text, but the board might behave otherwise
                line += c
            if "OpenBCI" in line:
                return True
        return False

    def print_register_settings(self):
        self.ser.write(b'?')
        time.sleep(0.5)
        self.print_incoming_text()

    # DEBBUGING: Prints individual incoming bytes
    #
    def print_bytes_in(self):
        if not self.streaming:
            self.ser.write(b'b')
            self.streaming = True
        while self.streaming:
            print(struct.unpack('B', self.ser.read())[0])

            '''Incoming Packet Structure:
          Start Byte(1)|Sample ID(1)|Channel Data(24)|Aux Data(6)|End Byte(1)
          0xA0|0-255|8, 3-byte signed ints|3 2-byte signed ints|0xC0'''

    def print_packets_in(self):
        while self.streaming:
            b = struct.unpack('B', self.ser.read())[0]

            if b == START_BYTE:
                self.attempt_reconnect = False
                if skipped_str:
                    logging.debug('SKIPPED\n' + skipped_str + '\nSKIPPED')
                    skipped_str = ''

                packet_str = "%03d" % (b) + '|'
                b = struct.unpack('B', self.ser.read())[0]
                packet_str = packet_str + "%03d" % (b) + '|'

                # data channels
                for i in range(24 - 1):
                    b = struct.unpack('B', self.ser.read())[0]
                    packet_str = packet_str + '.' + "%03d" % (b)

                b = struct.unpack('B', self.ser.read())[0]
                packet_str = packet_str + '.' + "%03d" % (b) + '|'

                # aux channels
                for i in range(6 - 1):
                    b = struct.unpack('B', self.ser.read())[0]
                    packet_str = packet_str + '.' + "%03d" % (b)

                b = struct.unpack('B', self.ser.read())[0]
                packet_str = packet_str + '.' + "%03d" % (b) + '|'

                # end byte
                b = struct.unpack('B', self.ser.read())[0]

                # Valid Packet
                if b == END_BYTE:
                    packet_str = packet_str + '.' + "%03d" % (b) + '|VAL'
                    print(packet_str)
                    # logging.debug(packet_str)

                # Invalid Packet
                else:
                    packet_str = packet_str + '.' + "%03d" % (b) + '|INV'
                    # Reset
                    self.attempt_reconnect = True


            else:
                print(b)
                if b == END_BYTE:
                    skipped_str = skipped_str + '|END|'
                else:
                    skipped_str = skipped_str + "%03d" % (b) + '.'

            if self.attempt_reconnect and (timeit.default_timer() - self.last_reconnect) > self.reconnect_freq:
                self.last_reconnect = timeit.default_timer()
                self.warn('Reconnecting')
                self.reconnect()

    def check_connection(self, interval=2, max_packets_to_skip=10):
        # stop checking when we're no longer streaming
        if not self.streaming:
            return
        # check number of dropped packages and establish connection problem if too large
        if self.packets_dropped > max_packets_to_skip:
            # if error, attempt to reconect
            self.reconnect()
        # check again again in 2 seconds
        threading.Timer(interval, self.check_connection).start()

    def reconnect(self):
        self.packets_dropped = 0
        self.warn('Reconnecting')
        self.stop()
        time.sleep(0.5)
        self.ser.write(b'v')
        time.sleep(0.5)
        self.ser.write(b'b')
        time.sleep(0.5)
        self.streaming = True
        # self.attempt_reconnect = False

    # Adds a filter at 60hz to cancel out ambient electrical noise
    #
    def enable_filters(self):
        self.ser.write(b'f')
        self.filtering_data = True

    #
    #
    def disable_filters(self):
        self.ser.write(b'g')
        self.filtering_data = False

    def test_signal(self, signal):
        """ Enable / disable test signal """
        if signal == 0:
            self.ser.write(b'0')
            self.warn("Connecting all pins to ground")
        elif signal == 1:
            self.ser.write(b'p')
            self.warn("Connecting all pins to Vcc")
        elif signal == 2:
            self.ser.write(b'-')
            self.warn("Connecting pins to low frequency 1x amp signal")
        elif signal == 3:
            self.ser.write(b'=')
            self.warn("Connecting pins to high frequency 1x amp signal")
        elif signal == 4:
            self.ser.write(b'[')
            self.warn("Connecting pins to low frequency 2x amp signal")
        elif signal == 5:
            self.ser.write(b']')
            self.warn("Connecting pins to high frequency 2x amp signal")
        else:
            self.warn("%s is not a known test signal. Valid signals go from 0-5" % (signal))

    def set_channel(self, channel, toggle_position):
        """ Enable / disable channels """
        # Commands to set toggle to on position
        if toggle_position == 1:
            if channel is 1:
                self.ser.write(b'!')
            if channel is 2:
                self.ser.write(b'@')
            if channel is 3:
                self.ser.write(b'#')
            if channel is 4:
                self.ser.write(b'$')
            if channel is 5:
                self.ser.write(b'%')
            if channel is 6:
                self.ser.write(b'^')
            if channel is 7:
                self.ser.write(b'&')
            if channel is 8:
                self.ser.write(b'*')
            if channel is 9 and cfg.daisyBoard:
                self.ser.write(b'Q')
            if channel is 10 and cfg.daisyBoard:
                self.ser.write(b'W')
            if channel is 11 and cfg.daisyBoard:
                self.ser.write(b'E')
            if channel is 12 and cfg.daisyBoard:
                self.ser.write(b'R')
            if channel is 13 and cfg.daisyBoard:
                self.ser.write(b'T')
            if channel is 14 and cfg.daisyBoard:
                self.ser.write(b'Y')
            if channel is 15 and cfg.daisyBoard:
                self.ser.write(b'U')
            if channel is 16 and cfg.daisyBoard:
                self.ser.write(b'I')
        # Commands to set toggle to off position
        elif toggle_position == 0:
            if channel is 1:
                self.ser.write(b'1')
            if channel is 2:
                self.ser.write(b'2')
            if channel is 3:
                self.ser.write(b'3')
            if channel is 4:
                self.ser.write(b'4')
            if channel is 5:
                self.ser.write(b'5')
            if channel is 6:
                self.ser.write(b'6')
            if channel is 7:
                self.ser.write(b'7')
            if channel is 8:
                self.ser.write(b'8')
            if channel is 9 and cfg.daisyBoard:
                self.ser.write(b'q')
            if channel is 10 and cfg.daisyBoard:
                self.ser.write(b'w')
            if channel is 11 and cfg.daisyBoard:
                self.ser.write(b'e')
            if channel is 12 and cfg.daisyBoard:
                self.ser.write(b'r')
            if channel is 13 and cfg.daisyBoard:
                self.ser.write(b't')
            if channel is 14 and cfg.daisyBoard:
                self.ser.write(b'y')
            if channel is 15 and cfg.daisyBoard:
                self.ser.write(b'u')
            if channel is 16 and cfg.daisyBoard:
                self.ser.write(b'i')

    #
    # This method is used to find the serial port connected to the OpenBCI headware. This is
    # used when the AUTO setting is used when selecting port in the GUI.
    #
    def find_port(self):
        #
        # Finds the serial port names. The port addresses are different on different
        # platforms.
        #
        if sys.platform.startswith('study_window'):
            self.gui.log_mess(dict.get_string(self, 'checkwin'))
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            self.gui.log_mess(dict.get_string(self, 'checklin'))
            ports = glob.glob('/dev/ttyUSB*')
        elif sys.platform.startswith('darwin'):
            self.gui.log_mess(dict.get_string(self, 'checkmac'))
            ports = glob.glob('/dev/tty.usbserial*')
        else:
            raise EnvironmentError('Error finding ports on your operating system')

        openbci_port = ''
        for port in ports:
            try:
                s = serial.Serial(port = cfg.portUsed,
                                  baudrate = cfg.baudrate,
                                  timeout = cfg.timeoutt)
                s.write(b'v')
                openbci_serial = self.openbci_id(s)
                s.close()
                if openbci_serial:
                    openbci_port = port
            except (OSError, serial.SerialException):
                pass
        if openbci_port == '':
            raise OSError('noport')
        else:
            return openbci_port


class OpenBCISample(object):
    """Object encapulsating a single sample from the OpenBCI board. NB: dummy imp for plugin compatiblity"""

    def __init__(self, packet_id, channel_data, aux_data):
        self.id = packet_id
        self.channel_data = channel_data
        self.aux_data = aux_data
        self.imp_data = []

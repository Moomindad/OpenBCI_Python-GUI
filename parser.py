import argparse

class settings(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="OpenBCI 'user'")


    def setBoard(self, board):

        self.parser.add_argument('--board', default="cyton",
                            help="Choose between [cyton] and [ganglion] boards.")
        parser.add_argument('-i', '--info', metavar='PLUGIN',
                            help="Show more information about a plugin.")
        parser.add_argument('-p', '--port',
                            help="For Cyton, port to connect to OpenBCI Dongle " +
                                 "( ex /dev/ttyUSB0 or /dev/tty.usbserial-* ). For Ganglion, MAC address of the board. For both, AUTO to attempt auto-detection.")
        parser.set_defaults(port="AUTO")
        parser.add_argument('--no-filtering', dest='filtering',
                            action='store_false',
                            help="Disable notch filtering")
        parser.set_defaults(filtering=True)
        parser.add_argument('-dic', '--daisy', dest='daisy',
                            action='store_true',
                            help="Force daisy mode (cyton board)")
        parser.add_argument('-x', '--aux', dest='aux',
                            action='store_true',
                            help="Enable accelerometer/AUX data (ganglion board)")
        # first argument: plugin name, then parameters for plugin
        parser.add_argument('-a', '--add', metavar=('PLUGIN', 'PARAM'),
                            action='append', nargs='+',
                            help="Select which plugins to activate and set parameters.")
        parser.add_argument('--log', dest='log', action='store_true',
                            help="Log program")
        parser.add_argument('--plugins-path', dest='plugins_path', nargs='+',
                            help="Additional path(s) to look for plugins")

        parser.set_defaults(daisy=False, log=False)

        args = parser.parse_args()

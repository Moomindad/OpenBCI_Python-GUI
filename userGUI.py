#!/usr/bin/env python3.6
"""
This is a version of the Open BCI python kit, with a rudimentary Graphic user interface, instead of the
argument based command line version distributed by OpenBCI. Most of the communication code is derived from
the original implementation.

September 13 2017
@author Lars Oestreicher

"""
# ===================
# Imports
# ===================
#
# Imports for OpenBCI
#
import logging
#
# Imports for the GUI handling
#
from tkinter import *
from tkinter import ttk

# The yapsy Pluginmanager facilitates the use of plugins. See Plugin directory.
#
from yapsy.PluginManager import PluginManager

# Local modules
#
# Importing two static objects.
#
from dictionary import Dictionary as dict

import settings

from Utilities import *

import controller as ctrl

# This import will be overridden later in the application.
#
import open_bci_v4 as bci

# ==============================================================================
# Main script beginning
# ==============================================================================
#
# Load the plugins from the plugin directory.
#
#
class UserGUI(object):

    __pluginSpace__ = None

    def __init__(self):

        # Initialising the plugins
        #
        self.manager = PluginManager()    # Yapsy pluginmanager is used for plugins.
        self.plugins_paths = ["plugins"]  # Make sure the path for the plugins works
        self.manager.setPluginPlaces(self.plugins_paths)
        self.manager.collectPlugins()

        # A list is used to keep track of the checkboxes for the channels of the Daisy board
        #
        self.dchancheckboxes = []

        # This variable will be set later in the program, when we know the type of board used.
        #
        self.ctr = None

        self.sets = settings.BCIsettings()

        # ========================
        # Create window instance
        #
        self.win = tk.Tk()
        self.win.title(dict.get_string('wintitle'))
        #
        # ==========================
        # Set minimal logging level
        #
        logging.basicConfig(level=logging.ERROR)
        #
        # =========================
        # Creating the GUI
        # =========================
        #
        # =========================
        # Create framed containers to hold widgets
        #
        # Plugin selection
        #
        self.labelsFrame1 = ttk.LabelFrame(self.win, text='')
        self.labelsFrame1.grid(column=0, row=0, padx=20, pady=5, sticky=tk.N)

        # Port selection
        #
        self.labelsFrame2 = ttk.LabelFrame(self.win, text='')
        self.labelsFrame2.grid(column=0, row=1, padx=20, pady=5, sticky="WE")

        # Board type selection
        #
        self.labelsFrame3 = ttk.LabelFrame(self.win, text='')
        self.labelsFrame3.grid(column=1, row=0, padx=20, pady=5, sticky=tk.N)

        # Message window for system messages.
        #
        self.labelsFrame4 = ttk.LabelFrame(self.win, text='')
        self.labelsFrame4.grid(column=4, row=0, padx=20, pady=5, sticky=tk.N)

        # Enable logging
        #
        self.labelsFrame5 = ttk.LabelFrame(self.win, text='')
        self.labelsFrame5.grid(column=1, row=1, padx=20, pady=5, sticky=tk.N)

        # Selecting active channels
        #
        self.labelsFrame6 = ttk.LabelFrame(self.win, text='')
        self.labelsFrame6.grid(column=2, row=0, columnspan=2, padx=20, pady=5, sticky=tk.N)

        # Space for information from plugins.
        #
        self.pluginsFrame = ttk.LabelFrame(self.win, text="Plugin settings")
        self.pluginsFrame.grid(column=0, row=6, padx=20, columnspan=5, sticky=tk.S)



        # Using a trick to let the plugins know about the window for plugin settings.
        # We will normally just have a single window instance for each run.
        #
        UserGUI.__plugin_space__ = self.pluginsFrame


        # =========================
        # Add a text field for messages from the Open BCI module.
        #
        # TODO: Fix the scrollbar
        #
        self.scr = Scrollbar(self.labelsFrame4)
        self.logWin = tk.Text(self.labelsFrame4, height=20, width=50)
        self.scr.configure(command=self.logWin.yview)
        self.logWin.configure(yscrollcommand=self.scr.set)
        self.logWin.grid(column=0, row=1)

        # =========================
        # Create and add Labels
        #
        self.aLabel = ttk.Label(self.labelsFrame2, text=dict.get_string('selport'))
        self.aLabel.grid(column=0, row=0, sticky="WE")

        self.bLabel = ttk.Label(self.labelsFrame1, text=dict.get_string('plugs'))
        self.bLabel.grid(column=0, row=0)

        self.cLabel = ttk.Label(self.labelsFrame1, text=dict.get_string('addargs'))
        self.cLabel.grid(column=1, row=0, columnspan=2)

        self.dLabel = ttk.Label(self.labelsFrame3, text=dict.get_string('board'))
        self.dLabel.grid(column=0, row=0, columnspan=2)

        self.eLabel = ttk.Label(self.labelsFrame4, text=dict.get_string('logmess'))
        self.eLabel.grid(column=0, row=0)

        self.fLabel = ttk.Label(self.labelsFrame6, text=dict.get_string('selchan'))
        self.fLabel.grid(column=0, row=0)

        self.gLabel = ttk.Label(self.labelsFrame6, text=dict.get_string('cychan'))
        self.gLabel.grid(column=0, row=1, sticky="W")

        self.hLabel = ttk.Label(self.labelsFrame6, text=dict.get_string('daisychan'))
        self.hLabel.grid(column=1, row=1, sticky="W")

        self.init = ttk.Button(self.win, text=dict.get_string('init'), command=self.connect_board)
        self.init.grid(column=3, row=1, padx=20, pady=20)

        self.spacer = ttk.Label(self.pluginsFrame, text="")
        self.spacer.grid(column=0, row=0, padx=25)

        # Variables for the button results
        #
        self.board = tk.IntVar()  # Main board
        self.dboard = tk.BooleanVar()  # Daisy board
        self.logP = tk.BooleanVar()  # Logging enabled

        # Check which board type we are using. Ganglion or Cyton with ot without Daisy
        #
        self.ganglionBoard = tk.Radiobutton(self.labelsFrame3, text='Ganglion', variable=self.board,
                                            command=self.rb_detected, value=1)
        self.cytonBoard = tk.Radiobutton(self.labelsFrame3, text='Cyton', variable=self.board, command=self.rb_detected,
                                         value=2)
        self.daisyBoard = tk.Checkbutton(self.labelsFrame3, text='With Daisy',
                                         variable=self.dboard, command=self.rb_detected)

        self.cytonBoard.grid(column=0, row=2, columnspan=2, sticky=tk.W)
        self.ganglionBoard.grid(column=0, row=1, columnspan=2, sticky=tk.W)
        self.daisyBoard.grid(column=1, row=3, sticky=tk.W)

        self.logging = tk.Checkbutton(self.labelsFrame5, text=dict.get_string('log'), variable=self.logP,
                                      command=self.log_enabled)
        self.logging.grid(column=0, row=0)

        # A Combobox is used to select the port.
        #
        self.portVal = tk.StringVar()

        self.aCombobox = ttk.Combobox(self.labelsFrame2,
                                      textvariable=self.portVal,
                                      values=getBluetToothDevices())  # this function is in file Utilities.py
        self.aCombobox.bind("<<ComboboxSelected>>", self.set_port)
        self.aCombobox.grid(column=0, row=1, sticky="WE")
        self.aCombobox.current(0)
        self.set_port("test")

        # Make sure that Cytonboard is selected by default.
        #
        self.cytonBoard.invoke()

        # =========================
        # Adding tooltips to the GUI widgets.
        #
        createToolTip(self.aCombobox, dict.get_string('tooltipport'))
        createToolTip(self.dLabel, dict.get_string('tooltipboard'))
        createToolTip(self.labelsFrame4, dict.get_string('tooltipmess'))

        # ==============================================================================
        #  Creating all the checkbutton widgets for choosing the channels on the board(s)
        #
        self.chan_var = []
        self.dchan_var = []
        self.chan_val = []
        self.dchan_val = []

        for chan in [1, 2, 3, 4, 5, 6, 7, 8]:
            name = "Channel: " + str(chan)
            self.chan_var.append(name)
            dname = "Channel: " + str(8 + chan)
            self.dchan_var.append(dname)

            self.chan_val.append(IntVar())
            self.chan_val[chan - 1].set(self.sets.get_channels()[chan - 1])

            self.dchan_val.append(IntVar())
            self.dchan_val[chan - 1].set(self.sets.get_dchannels()[chan - 1])

            chan_check = tk.Checkbutton(self.labelsFrame6, text=name, variable=self.chan_val[chan - 1])
            chan_check.grid(row=chan + 1, column=0, sticky=tk.W)

            if self.dboard.get():
                disable_state = 'active'
            else:
                disable_state = 'disabled'

            dchan_check = tk.Checkbutton(self.labelsFrame6, text=dname,
                                         variable=self.dchan_val[chan - 1], state=disable_state)
            dchan_check.grid(row=chan + 1, column=1, sticky=tk.W)
            self.dchancheckboxes.append(dchan_check)

        print(self.chan_val)

        # ==============================================================================
        #  Creating all the checkbutton widgets for choosing the plugins within one loop
        #
        plugins = self.manager.getAllPlugins()
        #
        # Initialising the arrays storing the handles for the checkbuttons for the plugins
        # and their arguments.
        #
        # The plugin_var array makes each checkbutton react with its own name.
        # The arg_var array keeps the arguments (all together as one single argument String).
        #
        self.plug_checks = []
        self.plugin_var = []
        self.arg_var = []
        #
        self.checkbox_num = IntVar()
        #
        # Loop counters can still be needed.
        #
        i = 0  # Initiating the loop counter
        newVar = ''
        #
        # Go through all the plugins and render them into a list of items which can be used to
        # address the contents of the selected items.
        #
        # On-off value is retrieved by using the following (sample): self.plug_checks[2].get()
        #
        # We want the plugins to appear in the same order every time.
        #
        plugins = sorted(plugins, key=lambda plugin: plugin.name)
        for plugin in plugins:
            name = plugin.name
            self.plugin_var.append(name)
            self.plug_checks.append(tk.IntVar())
            cur_check = tk.Checkbutton(self.labelsFrame1,
                                       text=name,
                                       variable=self.plug_checks[i],
                                       command=self.collect_plugins)
            cur_check.grid(row=i + 1, column=0, sticky=tk.W)
            cur_arg = Entry(self.labelsFrame1)
            cur_arg.grid(row=i + 1, column=1, sticky=tk.W)
            self.arg_var.append(cur_arg)

            # The print  plugin is selected by default.
            #
            if name == "print":
                cur_check.select()
            print(self.plug_checks[i].get())
            i = i + 1
        self.collect_plugins()

        # ==========================
        # Adding menus
        # ==========================

        # Creating a Menu Bar
        #
        self.menuBar = Menu(self.win)
        self.win.config(menu=self.menuBar)

        # Add menu items
        #
        self.fileMenu = Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="New Recording", command=self.new_rec)
        self.fileMenu.add_command(label="Save Recording", command=self.save_rec, accelerator="Cmd+S")
        self.fileMenu.add_command(label="Reset", command=self.reset)
        self.fileMenu.add_command(label="Exit", command=quit)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        # Add an actions menu
        #
        self.actionMenu = Menu(self.menuBar, tearoff=1)
        self.actionMenu.add_command(label="Initialise board", command=self.connect_board, accelerator="Cmd+I")
        self.actionMenu.add_command(label="Start streaming", command=self.start_streaming, accelerator="Cmd+B")
        self.actionMenu.add_command(label="Stop streaming", command=self.stop_streaming, accelerator="Cmd+K")
        self.menuBar.add_cascade(label="Actions", menu=self.actionMenu)

        # Add a utilities menu
        #
        self.utilMenu = Menu(self.menuBar, tearoff=0)
        self.utilMenu.add_command(label="Save Settings", command=self.save_settings)
        self.utilMenu.add_command(label="Restore Settings", command=self.restore_settings)
        self.menuBar.add_cascade(label="Utilities", menu=self.utilMenu)

        # Add another Menu to the Menu Bar and an item
        #
        self.helpMenu = Menu(self.menuBar, tearoff=0)
        self.helpMenu.add_command(label="About")
        self.menuBar.add_cascade(label="Help", menu=self.helpMenu)

        self.log_mess("GUI Ready!")

    # ===============
    # Method used to set the board type from the GUI. The selected board type is stored in the
    # settings object.
    #
    def rb_detected(self):
        #
        # First we try for the Cyton board, and then set check for the Daisy board addition
        #
        if self.board.get() == 2:
            self.sets.set_board_type("Cyton")
            self.sets.set_daisy(self.dboard.get())

            # If daisy board is not used, we can't use those channels.
            #
            if self.sets.get_daisy():
                for chan in self.dchancheckboxes:
                    chan.config(state="active")
            else:
                for chan in self.dchancheckboxes:
                    chan.config(state="disabled")
            #
            # A little unusual way to choose implementation but it works. We should not normally import anything here
            # in the file. See also the alternative import for ganglion as bci below.
            #
            # Note that the original import bci will be shadowed in this statement; this is
            # intentional. This way we will select the proper processing code for the available
            # board types (currently Cyton or Ganglion).
            #
            import open_bci_v4 as bci

            self.ctr = ctrl.Controller(self, bci, self.sets)
        #
        # Next we try for the ganglion board (which unfortunately does not work for the mac)
        # due to problems with the Bluepy library.
        #
        if self.board.get() == 1:
            #
            import open_bci_ganglion as bci
            self.ctr = ctrl.Controller(self, bci, self.sets)
            #
            self.sets.set_daisy(False)
            self.sets.set_board_type("Ganglion")
            # TODO: FIX THE BLUETOOTH LOW ENERGY LIBRARY for THE GANGLION BOARD
            # The BluePy Library does not work in the Mac Python environment.
            #
            self.log_mess(dict.get_string('nogang'))
            self.cytonBoard.invoke()

            # TODO: see if it is possible to also hook up a MindWave Mobile device to the same User interface.
            # This might be possible, but tricky, since the devices are very different in complexity.
            #

    # We have to define a function to create the OpenBCI client. This has to be done here, in order to
    # provide the proper scope for the import. Do not move this method. This method is called from the
    # Button with the 'init' text.
    #
    # Note that bci can refer to two different types of boards, ganglion or cyton.
    #
    #
    def prepare_settings(self):
        #
        # First we have to get the Interface data stored in the settings.
        #
        self.collect_settings_data()

        # Since the type of board is selected in the user interface but the controller is repsonsible for its use, we
        # send the bci variable as it is without instantiating the bard here.
        #
        self.ctr = ctrl.Controller(self, bci)


    # ===============
    # Menu commands
    #
    # TODO implement actions to the commands.
    #
    def new_rec(self):
        pass

    def reset(self):
        pass

    def save_rec(self):
        pass

    def set_port(self, event):
        self.log_mess(self.portVal.get())
        self.sets.set_port(self.portVal.get())

    def stop_streaming(self):
        self.ctr.stop()

    # Transfer functions, that send actions to the controller.
    #
    def connect_board(self):
        self.collect_settings_data()
        self.ctr.connect_board()

    def start_streaming(self):
        self.ctr.start_streaming()

        # Writes message to the message panel.
    #
    def log_mess(self, message, status=NORMAL):
        self.logWin.insert(END, message + "\n")

    def initialise(self):
        pass

    def log_enabled(self):
        if self.logP.get():
            self.sets.set_logging(TRUE)
            self.log_mess("Logging enabled")
        else:
            self.sets.set_logging(FALSE)
            self.log_mess("Logging disabled")

    # ===========================================
    # Collecting all settings from the interface.
    #
    def collect_settings_data(self):

        self.collect_channels()
        self.collect_plugins()

    # ==========================================
    # Collecting all the plugins in a suitable format.
    #
    def collect_plugins(self):
        plugs = []
        for i in range(0, len(self.plugin_var) ):
            if self.plug_checks[i].get() == 1:
                if self.arg_var[i].get() == '':
                    plugs.append([self.plugin_var[i]])
                else:
                    plugs.append([self.plugin_var[i], self.arg_var[i].get()])

        self.sets.set_plugins(plugs)

        print(self.sets.get_plugins())

    def get_plugin_space(self):
        return self.pluginsFrame

    # ===========================================
    # Set the selected channels both for daisy and for the main
    # board.
    #
    def collect_channels(self):
        chans = []
        dchans = []

        for var in self.chan_val:
            if var.get() == 1:
                chans.append(1)
            else:
                chans.append(0)
        for var in self.dchan_val:
            if var.get() == 1:
                dchans.append(1)
            else:
                dchans.append(0)

        self.sets.set_channels(chans)
        self.sets.set_dchannels(dchans)
        print(chans)
        print(dchans)


    # ==================================================
    # We can store the settings if they are complicated.
    #
    def save_settings(self):

        self.sets.save_settings()

    # To restore the settings we have to use a class method, since we might want to use it as a startup.
    # This is why there is an argument (42) in the class reference, rather than an empty parenthesis.
    #
    def restore_settings(self):

        self.sets.restore_settings()
        #
        # TODO: add code, so that the restored settings will be added back to the window on start.
        #

    # =================
    # To display the window we start the mainloop
    #
    def start(self):
        self.win.mainloop()

    def handle_sample(sample):
        print(sample.channel_data)


# ==========================
# Initialising the class
#
eeg = UserGUI()


# ==========================
# Starting the application
#
eeg.start()

# ==========================
# END of FILE
# ==========================



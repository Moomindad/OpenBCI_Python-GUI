#!/usr/bin/env python3.6
#
# IMPORT
#
import logging

from yapsy.PluginManager import PluginManager

# Importing two static objects.
#
from dictionary import Dictionary as dict

# =======================
# Enable loading of the plugins from the plugin directory.
#
manager = PluginManager()

# Enable logging of errors
#
logging.basicConfig(level=logging.ERROR)


class Controller(object):
    """
    The controller is responsible for handling all the preparations of the reader, and the reading from the model.
    The model is in the bci board, given as input to the class.

    """

    def __init__(self, gui, bd, sets):

        # Initialising the plugin manager
        #
        self.manager = PluginManager()      # Yapsy pluginmanager is used for plugins.
        self.plugins_paths = ["plugins"]    # Make sure the path for the plugins works
        self.manager.setPluginPlaces(self.plugins_paths)
        self.manager.collectPlugins()

        #
        # Setting need-to-know variables.
        #
        self.gui = gui

        # Here is the instantiation of the board.
        #
        self.board = bd

        self.settings = sets

        # Set of callback functions (plug-ins) that have been acitvated.
        #
        self.callback_list = []
        self.plug_list = []




    # ============================================================
    # Internal functions for the controller. Most of these will be activated from the GUI. These are marked by the
    # type of initialisation, e.g. <MENU>
    #

    # Initialisation for the board, and setting it up for commands.
    #
    # <MENU, BUTTON>
    #
    def connect_board(self):
        self.model = self.board.OpenBCIBoard(self, self.gui, self.settings)
        self.activate_plugins()

    # <MENU>
    #
    def start_streaming(self):
        self.model.start_streaming_thread(self.callback_list)

    # <MENU>
    #
    def set_channels(self):
        pass
    def stop(self):
        self.model.stop()

    # Initialising the active channels.
    #



    # Method used to activate the plugins. If any plugin is not responding properly, an error message is generated.
    # This function is used initially, but can also be used during a run, for example to add new plugins,
    # if something interesting occurs.
    #
    def activate_plugins(self):

        self.plug_list = []
        self.callback_list = []

        # Fetch selected plugins from settings, try to activate them, add to the list if OK
        #
        plugs = self.settings.get_plugins()


        for plug_candidate in plugs:

            # first value: plugin name, then optional arguments
            #
            plug_name = plug_candidate[0]
            plug_args = plug_candidate[1:]

            # Try to find name
            #
            plug = self.manager.getPluginByName(plug_name)

            if plug == None:

                # eg: if an import failS inside a plugin, yapsy will skip it
                #
                print("Error: [ " + plug_name + " ] not found or could not be loaded. Check name and requirements.")

            else:
                print("\nActivating [ " + plug_name + " ] plugin...")
                if not plug.plugin_object.pre_activate(plug_args,
                                                       sample_rate=self.model.get_sample_rate(),
                                                       eeg_channels=self.model.get_nb_eeg_channels(),
                                                       aux_channels=self.model.get_nb_aux_channels(),
                                                       imp_channels=self.model.get_nb_imp_channels()):
                    print("Error while activating [ " + plug_name + " ], check output for more info.")
                else:
                    print("Plugin [ " + plug_name + "] added to the list")
                    self.plug_list.append(plug.plugin_object)
                    self.callback_list.append(plug.plugin_object)

        print(self.callback_list)

    # The deactivation of plugins is necessary for a clean closing of files, etc.
    #
    def clean_up(self):
        self.model.disconnect()
        print(dict.get_string('deactivate_plug'))
        for plug in self.plug_list:
            plug.deactivate()
        print(dict.get_string('exiting'))

# =================================================
# =================================================
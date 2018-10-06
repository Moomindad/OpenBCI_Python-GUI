"""
Contains values that should be accessible by all functions that need common values. Even if they are previously undefined
dummy values should be given here. These variables are all accessed as globals.
"""

# DEFAULT SETTINGS.
#
boardType = "Cyton"

# Since not all run with daisyboards, we put the default to no daisyboard.
#
daisyBoard = False

# The available 16 channels is more than enough. All Cyton channels active to start with.
# Daisy board channels are issued as non-active by default.
#
channels = [1, 1, 1, 1, 1, 1, 1, 1]
dchannels = [0, 0, 0, 0, 0, 0, 0, 0, 0]
portUsed = None
filteringEnabled = True
logging = False
baudrate = 115200

debug = True

# Impedance and auxiliaries are not used currently.
#
impedance = False
aux = False,

# Reading timeout is set to 100 ms
#
timeout = 100

scaling = 0

# This is used to stop streaming when needed.
#
streaming = False

# The default plugin is the one printing on the console.
#
plugins = [['print']]

# Temporary settings are set to null, initially.

eeg = None

main_window = None
pluginSpace = None

plugin_menu = None

# This variable keeps the currently used version of openBCI board
#
current_board = None

# ===================
# PLUGIN SETTINGS
#
# TRIGGER
# ===================
# SEMAPHORE VARIABLES
#

plugin_instance = None

study_running = False
image_shown = False
image_type = None
new_image = False
collecting = False

image_number = 0

sensornumber = 16  # This also equals the number of rows in a packet.

# ========================================================================
# The array is used to access the trigger values quickly.
# Example values are:

# == No stimuli

# 0 - black screen before each stimuli presentation

# == Perception phase

# 1 - stimuli presentation -- 0,0 - 0,1 s
# 2 - stimuli presentation -- 0,1 - 0,2 s

# == Recognition phase

# 3 - stimuli presentation -- 0,2 - 0,3 s
# 4 - stimuli presentation -- 0,3 - 0,4 s

# == Cognition phase

# 5 - stimuli presentation -- 0,4 - 0,5
# 6 - stimuli presentation -- 0,5 - 0,6

# == Permanent showing the stimuli

# 7 - permanent stimuli -- 0,6 -

triggerval = [[1, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 0
              [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],  # 1
              [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],  # 2
              [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],  # 3
              [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],  # 4
              [0, 0, 0, 0, 0, 1, 0, 0, 0, 0],  # 5
              [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],  # 6
              [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],  # 7
              [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],  # 8
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # 9
              [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # 10
              ]

# We want to put the same values in string format, just in case.'
#
triggervalstr = ["[1, 0, 0, 0, 0, 0, 0, 0, 0, 0]",  # 0
                 "[0, 1, 0, 0, 0, 0, 0, 0, 0, 0]",  # 1
                 "[0, 0, 1, 0, 0, 0, 0, 0, 0, 0]",  # 2
                 "[0, 0, 0, 1, 0, 0, 0, 0, 0, 0]",  # 3
                 "[0, 0, 0, 0, 1, 0, 0, 0, 0, 0]",  # 4
                 "[0, 0, 0, 0, 0, 1, 0, 0, 0, 0]",  # 5
                 "[0, 0, 0, 0, 0, 0, 1, 0, 0, 0]",  # 6
                 "[0, 0, 0, 0, 0, 0, 0, 1, 0, 0]",  # 7
                 "[0, 0, 0, 0, 0, 0, 0, 0, 1, 0]",  # 8
                 "[0, 0, 0, 0, 0, 0, 0, 0, 0, 1]",  # 9
                 "[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]",  # 10
                 ]

collecting = False
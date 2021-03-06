#!/usr/bin/env python3.6
#
'''
Created on Jul 4, 2015

@author: Burkhard
'''
import subprocess
import sys
# ======================
# imports
# ======================
import tkinter as tk

debugging = True

# Adding tooltips to the various buttons and controls.
#
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    # Display text in tooltip window
    #
    def showtip(self, text):

        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))

        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "12", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


# ===================================================================
# Each tooltip is an instance of the tooltip class
#
def createToolTip(widget, text):
    toolTip = ToolTip(widget)

    def enter(event):
        toolTip.showtip(text)

    def leave(event):
        toolTip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


# ===================================================================
# Function to gather the available Bluetooth devices.
# ===================================================================
# Since the com ports are different on OSX and windows we need to make two
# different port definitions.
#
def getBluetToothDevices():
    if sys.platform == 'darwin':                # OS X
        p = subprocess.Popen("ls /dev/tty.*", stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
    else:
        if 'win' in sys.platform:             # Windows.
            output = ["COM3"]
            # TODO TOM check that this works for windows 64

    return output


def mybug(textlist):
    if debugging:
        for item in textlist:
            print(item)
            print('\n')


def debug(boolval):
    debugging = boolval
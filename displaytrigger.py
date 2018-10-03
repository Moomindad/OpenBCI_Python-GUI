from tkinter import *
from tkinter import ttk
import glob
from PIL import Image, ImageTk
import random

import config as cfg

#from yapsy.PluginManager import PluginManager

##############################
# Constant definitions
#
TIME = [
    3,
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


class StudyGui(object):

    def __init__(self):

        # Semaphores
        #
        cfg.study_running = False       # Indicates ongoing study
        cfg.image_shown = False         # Indicates whether an image is currently shown or not
        cfg.new_image = False           # Indicates whether a new image has been loaded or not

        # Will keep a list with all images in a random order.
        #
        self.ran_list = ()
        self.image_dict = {}

        # Create window instance, under the main window (since it is a plugin window).
        #
        self.study_window = Toplevel(cfg.main_window)
        self.study_window.title('EEG Study')
        self.img_counter = 0

        # Open the image used for the pause between images (normally a black screen)
        #
        self.im = glob.glob('./Images/Pause/*')
        self.black_screen = ImageTk.PhotoImage(Image.open(self.im[0]))

        # Create the containers to hold widgets
        #
        # Start button container
        #
        self.buttonFrame = ttk.Frame(self.study_window)
        self.buttonFrame.grid(column=2, row=2, padx=20, pady=5, sticky='S')

        # Plugin selection
        #
        self.labelsFrame1 = LabelFrame(self.study_window, background='white', text='Settings:')
        self.labelsFrame1.grid(column=0, row=0, padx=20, pady=5, sticky='N')

        # Port selection
        #
        self.labelsFrame2 = ttk.LabelFrame(self.study_window, text='')
        self.labelsFrame2.grid(column=0, row=1, padx=20, pady=5, sticky="WE")

        # Board type selection
        #
        self.labelsFrame3 = ttk.LabelFrame(self.study_window, text='')
        self.labelsFrame3.grid(column=1, row=0, padx=20, pady=5, sticky='N')

        # ==========================
        # Adding menus
        # ==========================
        #
        cfg.plugin_menu.add_command(label="Start Experiment", command=self.studyStart)
        cfg.plugin_menu.add_command(label="Reset Experiment", command=self.reset)

        # =====================
        # Adding settings dropdown menu
        # =====================
        # Dropdown menu for image selection
        #
        self.image_var = StringVar(self.study_window)
        self.image_var.set(IMAGES[0])            # Default value
        self.sel_images = OptionMenu(self.labelsFrame1, self.image_var, *IMAGES).grid(row=0, column=1, sticky=W)
        self.label_sel_img = Label(self.labelsFrame1, text="Select Images:").grid(column=0, row=0, sticky=W)

        # Dropdown menu for time selection
        #
        self.time_var = IntVar(self.study_window)
        self.time_var.set(TIME[0])               # Default value
        self.sel_time = OptionMenu(self.labelsFrame1, self.time_var, *TIME).grid(row=1, column=1, sticky=W)
        self.label_sel_time = Label(self.labelsFrame1, text="Select Time:", justify=LEFT).grid(row=1, column=0, sticky=W)

        # Radio buttons for order
        #
        self.order_var = IntVar()
        self.sel_order1 = Radiobutton(self.labelsFrame1, text="Set", variable = self.order_var, value = 0).grid(row=2, column=1, sticky=W)
        self.sel_order2 = Radiobutton(self.labelsFrame1, text="Random", variable = self.order_var, value = 1).grid(row=3, column=1, sticky=W)
        self.label_sel_order = Label(self.labelsFrame1, text="Select order:").grid(row=2, column=0, sticky=W)

        # Check button for pauses
        #
        self.pause_var = IntVar()
        self.pause_button = Checkbutton(self.labelsFrame1, text='Use black screen between images', variable=self.pause_var, pady=10)
        self.pause_button.grid(row=5,column=0, sticky=E)

        # Add startbutton
        #
        self.start_button = Button(self.buttonFrame, text='Start Study', padx=10, command=self.studyStart).grid(row=0, column=1)

        # Add quit study button
        #
        self.quit_button = Button(self.buttonFrame, text='Quit Study', padx=10, command=lambda: self.study_screen.destroy()).grid(row=0, column=0)

    def start(self):
        self.study_window.mainloop()

    def reset(self):
        self.study_window.quit()

    # Responsible for the connection between plugin and this program
    #
    def newImage(self):
        # TODO Connect to the "call" function in pl
        self.study = True

    # A semaphore is used to signal an image being shown or not.
    #
    def betweenImage(self):
        self.study = False

    # ====================================
    # Create a fullscreen Toplevel window
    # ====================================
    #
    def studyStart(self):

        def remove_instr(event=None):
            self.study_instructions.pack_forget()

        def start_study():
            cfg.eeg.start_streaming()         # Before we start, we start the streaming of data.
            show_image(event=None)

        def show_image(event=None):
            """
            This is the main function administrating the images and pauses.
            Interaction with the plugin is mostly done by semaphore variables in the config module.
            """
            # if not cfg.study_running:
            #     return

            # cfg.image_number = im_counter

            if self.order_var.get() == 0:                     # Show the images in the given order.
                if cfg.image_number < len(self.image_dict):
                        self.im = self.image_dict[str(cfg.image_number * 10)]
                        self.image_label.configure(image=self.im)
                        cfg.image_shown = True                # This will be set to false for black background inbetween
                        cfg.new_image = True                  # This will be reset by the first call
                        cfg.image_number += 1
                        self.study_screen.after(self.time_var.get() * 1000, showBlack, cfg.image_number)

            else:                                             # Use the randomised list
                if cfg.image_number < len(self.image_dict):
                    self.im = self.image_dict[self.ran_list[cfg.image_number]]
                    self.image_label.configure(image=self.im)
                    cfg.image_number += 1
                    self.study_screen.after(self.time_var.get() * 1000, showBlack, cfg.image_number)


        def randomize(self):
            key_list = list(self.image_dict.keys())
            random.shuffle(key_list)
            return key_list

        def showBlack(counter):
            if self.pause_var.get() == 1:
                cfg.image_shown = False  # Pause the stream while background is shown.
                self.image_label.configure(image=self.black_screen)
                if counter >= len(self.image_dict):
                    counter = 0
                self.study_screen.after(3000, show_image, counter)
            else:
                if counter >= len(self.image_dict):
                    counter = 0
                show_image(counter)

        def openImages(self):
            self.image_dir = glob.glob('./Images/%s/*' % self.image_var.get())
            for i in range(len(self.image_dir)):
                x = ImageTk.PhotoImage(Image.open(self.image_dir[i]))
                self.image_dict[str(i*10)] = x
            return self.image_dict

        def destroyWindow():
            self.study_screen.destroy()

        self.study_screen = Toplevel(bg='black')

        # Make sure the the window is in fullscreen mode.
        #
        self.w, self.h = self.study_screen.winfo_screenwidth(), self.study_screen.winfo_screenheight()
        self.study_screen.overrideredirect(1)
        self.study_screen.geometry("%dx%d+0+0" % (self.w, self.h))

        # Make the new window focused.
        #
        self.study_screen.focus_set()  # <-- move focus to this widget
        self.instr_txt='Welcome to my EEG study.\n\r You will be shown several screens of stimuli with ' \
                            ' a black screen in between.\n\r Please simply focus on the screen.\n\r\n\r ' \
                            'Press Enter to start the study.'

        # TODO externalise string

        # Write the study instructions
        #
        self.study_instructions = Label(self.study_screen, text=self.instr_txt)
        self.study_instructions.config(fg='white', bg='black', pady=500, font=('Palatino', 28))
        self.study_instructions.pack()
        self.image_label = Label(self.study_screen)
        self.image_label.pack()

        # Open the images and put into a list
        #
        self.image_dict = openImages(self)

        # Create a list of the random indexes that will be used in show_image
        #
        self.ran_list = randomize(self)

        # Remove the Label and start the study when Return is pressed
        #
        self.study_screen.bind('<Return>', remove_instr, start_study())

        #
        self.study_screen.bind("<Escape>", lambda e: destroyWindow())

# These will only be used here in case the StudyGUI is run as a standalone application
#
#eeg = StudyGui()  # läggs i collect-plugin
#
#
#eeg.start()       # läggs i collect-plugin


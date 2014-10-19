''' Module to handle the motorised focuser via an Arduino
'''

from Tkinter import N, S, E, W, HORIZONTAL, StringVar
import ttk

class Focuser(object):
    ''' Class to handle the user interface for interfacing with the focuser
        via the arduino.
    '''
    def __init__(self, frame):
        ''' Draw the frame and widgets and set up handlers.
        '''
        self.frame = frame
        self.com = StringVar()

        rframe = ttk.Frame(self.frame)
        rframe.grid(sticky=(N, S, E, W))

        sliders = ttk.Frame(rframe)
        sliders.grid(column=0, row=0, sticky=(N, E, W))
        sliders.columnconfigure(1, weight=3)

        self.__sliders(sliders)

        buttons = ttk.Frame(rframe)
        buttons.grid(column=0, row=1, sticky=(N, E, W))
        buttons.rowconfigure(0, weight=3)

        self.__buttons(buttons)

        comframe = ttk.Frame(rframe)
        comframe.grid(column=0, row=2, sticky=(N, E, W))
        comframe.rowconfigure(0, weight=3)

        self.__comport(comframe)

        notice = ttk.Label(rframe, text="THIS IS A PLACEHOLDER NOTEBOOK - " +
                           "NOT IMPLEMENTED")
        notice.grid()

    def __sliders(self, sliders):
        ''' Private function to handle the sliders.
        '''
        speed_text = ttk.Label(sliders, text="Motor Speed  ")
        speed_text.grid(column=0, row=0)
        speed_slider = ttk.Scale(sliders, orient=HORIZONTAL,
                                 length=500, from_=1.0, to=100.0)
        speed_slider.grid(column=1, row=0)
        pulse_text = ttk.Label(sliders, text="Pulse Time(ms)  ")
        pulse_text.grid(column=0, row=1)
        pulse_slider = ttk.Scale(sliders, orient=HORIZONTAL,
                                 length=500, from_=1.0, to=100.0)
        pulse_slider.grid(column=1, row=1)

    def __buttons(self, buttons):
        ''' Private function to handle the buttons.
        '''
        full_reverse = ttk.Button(buttons, text="Motor\nReverse\nFull")
        full_reverse.grid(column=0, row=0, padx=5, sticky=(N, S, E, W))
        click_hold_reverse = ttk.Button(buttons,
                                        text="Motor\nReverse\nClick/Hold")
        click_hold_reverse.grid(column=1, row=0, padx=5, sticky=(N, S, E, W))
        pulse_reverse = ttk.Button(buttons, text="Motor\nReverse\nPulse")
        pulse_reverse.grid(column=2, row=0, padx=5, sticky=(N, S, E, W))
        motor_off = ttk.Button(buttons, text="Motor Off")
        motor_off.grid(column=3, row=0, padx=5, sticky=(N, S, E, W))
        pulse = ttk.Button(buttons, text="Motor\nForward\nPulse")
        pulse.grid(column=4, row=0, padx=5, sticky=(N, S, E, W))
        click_hold = ttk.Button(buttons, text="Motor\nForward\nClick/Hold")
        click_hold.grid(column=5, row=0, padx=5, sticky=(N, S, E, W))
        full = ttk.Button(buttons, text="Motor\nReverse\nFull")
        full.grid(column=6, row=0, padx=5, sticky=(N, S, E, W))

    def __comport(self, comframe):
        ''' Private function to handle the COM port selector.
        '''
        label = ttk.Label(comframe, text="Select COM port: ")
        label.grid(column=0, row=0)
        com = ttk.Combobox(comframe, textvariable=self.com)
        com['values'] = ('COM6', 'COM7', 'COM8', 'COM9')
        com.grid(column=1, row=0)

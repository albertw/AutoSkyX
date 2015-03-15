''' Module to handle the motorised focuser via an Arduino
'''

import logging
from Tkinter import N, S, E, W, HORIZONTAL, StringVar, Tk
import ttk
import tkMessageBox

import arduino

log = logging.getLogger(__name__)


class Focuser(object):
    ''' Class to handle the user interface for interfacing with the focuser
        via the arduino.
    '''
    def __init__(self, frame):
        ''' Draw the frame and widgets and set up handlers.
        '''

        self.uno = arduino.Arduino()

        self.frame = frame
        self.comport = StringVar()

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

    def __sliders(self, sliders):
        ''' Private function to handle the sliders.
        '''
        speed_text = ttk.Label(sliders, text="Motor Speed  ")
        speed_text.grid(column=0, row=0)
        self.speed_slider = ttk.Scale(sliders, orient=HORIZONTAL,
                                      length=500, from_=1.0, to=255.0)
        self.speed_slider.grid(column=1, row=0)
        self.speed_slider.set(255)
        pulse_text = ttk.Label(sliders, text="Pulse Time(ms)  ")
        pulse_text.grid(column=0, row=1)
        self.pulse_slider = ttk.Scale(sliders, orient=HORIZONTAL,
                                      length=500, from_=1.0, to=1000.0)
        self.pulse_slider.grid(column=1, row=1)
        self.pulse_slider.set(30)

    def __buttons(self, buttons):
        ''' Private function to handle the buttons.
        '''
        full_reverse = ttk.Button(buttons, text="Motor\nReverse\nFull",
                                  command=self.__full_reverse)
        full_reverse.grid(column=0, row=0, padx=5, sticky=(N, S, E, W))
        # TODO These may not need to be self.
        self.click_hold_reverse = ttk.Button(buttons,
                                             text="Motor\nReverse\nClick/Hold",
                                             command=self.__click_reverse)
        self.click_hold_reverse.bind("<Button-1>", self.__click_reverse)
        self.click_hold_reverse.bind("<ButtonRelease-1>", self.__motor_off)
        self.click_hold_reverse.grid(column=1, row=0, padx=5,
                                     sticky=(N, S, E, W))
        pulse_reverse = ttk.Button(buttons, text="Motor\nReverse\nPulse",
                                   command=self.__pulse_reverse)
        pulse_reverse.grid(column=2, row=0, padx=5, sticky=(N, S, E, W))
        motor_off = ttk.Button(buttons, text="Motor Off",
                               command=self.__motor_off)
        motor_off.grid(column=3, row=0, padx=5, sticky=(N, S, E, W))
        pulse = ttk.Button(buttons, text="Motor\nForward\nPulse",
                           command=self.__pulse_forward)
        pulse.grid(column=4, row=0, padx=5, sticky=(N, S, E, W))
        self.click_hold = ttk.Button(buttons, text="Motor\nForward\nClick/Hold",
                                     command=self.__click_forward)
        self.click_hold.grid(column=5, row=0, padx=5, sticky=(N, S, E, W))
        self.click_hold_reverse.bind("<Button-1>", self.__click_forward)
        self.click_hold_reverse.bind("<ButtonRelease-1>", self.__motor_off)
        full = ttk.Button(buttons, text="Motor\nForward\nFull",
                          command=self.__full_forward)
        full.grid(column=6, row=0, padx=5, sticky=(N, S, E, W))

    def __full_reverse(self):
        self.uno.send_char("q")

    def __click_reverse(self, *args):
        self.uno.send_char("w")

    def __pulse_reverse(self):
        log.debug(self.uno.set_speed(self.speed_slider.get()))
        log.debug(self.uno.set_pulse_duration(self.pulse_slider.get()))
        log.debug(self.uno.send_char("e"))

    def __motor_off(self, *args):
        self.uno.send_char("r")

    def __pulse_forward(self):
        log.debug(self.uno.set_speed(self.speed_slider.get()))
        log.debug(self.uno.set_pulse_duration(self.pulse_slider.get()))
        log.debug(self.uno.send_char("t"))

    def __click_forward(self, *args):
        self.uno.send_char("y")

    def __full_forward(self):
        self.uno.send_char("u")

if __name__ == "__main__":
    ROOT = Tk()
    Focuser(ROOT)
    ROOT.mainloop()

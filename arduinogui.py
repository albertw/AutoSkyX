''' Module to handle the motorised focuser via an Arduino
'''

from Tkinter import N, S, E, W, HORIZONTAL, StringVar, Tk
import ttk
import tkMessageBox

import arduino


class ArduinoGUI(object):
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

        comframe = ttk.Frame(rframe)
        comframe.grid(column=0, row=2, sticky=(N, E, W))
        comframe.rowconfigure(0, weight=3)

        self.__comport(comframe)

    def __comport(self, comframe):
        ''' Private function to handle the COM port selector.
        '''
        self.comlabel = ttk.Label(comframe, text="Select COM port: ")
        self.comlabel.grid(column=0, row=0)
        self.com = ttk.Combobox(comframe, textvariable=self.comport)
        self.com['values'] = ('COM3', 'COM6', 'COM7', 'COM8', 'COM9')
        self.com.current(2)
        self.com.grid(column=1, row=0)
        self.connect = ttk.Button(comframe, text="Connect",
                                  command=self.__connect)
        self.connect.grid(column=2, row=0)

    def __connect(self):
        ''' Get the com port and call connect or disconnect if we are already
            connected
        '''
        if self.uno.isconnected():
            self.uno.disconnect()
            self.connect.config(text="Connect")
        else:
            try:
                self.uno.connect(self.comport.get())
                self.connect.config(text="Disconnect")
            except OSError, errmsg:
                tkMessageBox.showinfo("Arduino Error", str(errmsg) +
                                      "\nHint: Check the com port your " +
                                      "arduino is attached to.")


if __name__ == "__main__":
    ROOT = Tk()
    ArduinoGUI(ROOT)
    ROOT.mainloop()

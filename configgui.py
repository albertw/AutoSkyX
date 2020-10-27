''' Module to handle the motorised focuser via an Arduino
'''

from tkinter import N, S, E, W, HORIZONTAL, StringVar, Tk
import tkinter.ttk
import tkinter.messagebox

import arduino
import skyx
# TODO: SkyX Host
# TODO: Load/Save config
# TODO: default min altitude
# TODO: default exposure
# TODO: default duration
# TODO: debug toggle

class ConfigGUI(object):
    ''' Class to handle the user interface for interfacing with the focuser
        via the arduino.
    '''
    def __init__(self, frame):
        ''' Draw the frame and widgets and set up handlers.
        '''

        self.uno = arduino.Arduino()

        self.frame = frame
        self.comport = StringVar()
        self.skyxhost = StringVar()
        self.skyxhost.set("192.168.192.44")

        rframe = tkinter.ttk.Frame(self.frame)
        rframe.grid(sticky=(N, S, E, W))

        comframe = tkinter.ttk.Frame(rframe)
        comframe.grid(column=0, row=2, sticky=(N, E, W))
        comframe.rowconfigure(0, weight=3)

        self.__comport(comframe)

        skxlabel = tkinter.ttk.Label(comframe, text='SkyX Host:')
        skxlabel.grid(column=0, row=1, sticky=(W))
        skxentry = tkinter.ttk.Entry(comframe, textvariable=self.skyxhost)
        skxentry.grid(column=1, row=1, sticky=(W))
        setskyxbut = tkinter.ttk.Button(comframe,
                                text="Update SkyX hostname",
                                command=self._updateskyxhost)
        setskyxbut.grid(column=2, row=1, sticky=(W))

        
    def __comport(self, comframe):
        ''' Private function to handle the COM port selector.
        '''
        self.comlabel = tkinter.ttk.Label(comframe, text="Select COM port: ")
        self.comlabel.grid(column=0, row=0)
        self.com = tkinter.ttk.Combobox(comframe, textvariable=self.comport)
        self.com['values'] = ('COM3', 'COM6', 'COM7', 'COM8', 'COM9')
        self.com.current(2)
        self.com.grid(column=1, row=0)
        self.connect = tkinter.ttk.Button(comframe, text="Connect",
                                  command=self.__connect)
        self.connect.grid(column=2, row=0)

    def _updateskyxhost(self):
        ''' Update the host in the SkyX singleton
        '''
        sx = skyx.SkyXConnection()
        sx.reconfigure(host=self.skyxhost.get())
        
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
            except OSError as errmsg:
                tkinter.messagebox.showinfo("Arduino Error", str(errmsg) +
                                      "\nHint: Check the com port your " +
                                      "arduino is attached to.")


if __name__ == "__main__":
    ROOT = Tk()
    ConfigGUI(ROOT)
    ROOT.mainloop()

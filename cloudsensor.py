""" Module to implement the Arduino based cloud sensor

    Siren wav from http://soundbible.com/1577-Siren-Noise.html
"""

from tkinter import N, S, E, W, StringVar, Tk
import datetime
import logging
import math
from random import randint
import subprocess
import sys
import socket
import select
import tkinter.ttk

log = logging.getLogger(__name__)
templog = logging.getLogger('CloudData')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from arduino import Arduino

try:
    import winsound
except ImportError:
    # must not be windows...
    pass

# TODO: This should be in a config script along with server names etc.
# delay in ms to update temperatures
polldelay = 2000
offdelay = 500
serverdelay = 100


class CloudSensor(object):
    """ Cloud sensor notebook object"""

    def __init__(self, frame):
        """ initiate the window"""
        self.uno = Arduino()

        self.threshold = StringVar()
        self.threshold.set("90")

        self.frame = frame
        self.skytmphist = []
        self.ambtmphist = []
        self.timearray = []
        self.skytemp = None
        self.ambtemp = None
        self.fig = None
        self.canvas = None
        self.ax1 = None
        self.csmode = StringVar()
        self.socket = None
        self.mute = False
        self.mutebutton = None
        self.com = None
        self.stopbutton = None
        self.stop = True

        rframe = tkinter.ttk.Frame(self.frame)
        rframe.grid(sticky=(N, S, E, W))

        plot = tkinter.ttk.Frame(rframe)
        plot.grid(column=0, row=0, sticky=(N, E, W))
        plot.columnconfigure(1, weight=3)

        self.__plot(plot)

        info = tkinter.ttk.Frame(rframe)
        info.grid(column=1, row=0, sticky=(N, E, W))
        info.rowconfigure(0, weight=3)

        self.__info(info)

        self.updatetmp()
        self.network()

    def __plot(self, frame):
        """ Draw the plot of temperatures.
        """
        sframe = tkinter.ttk.Frame(frame)
        sframe.grid()
        self.fig = Figure(figsize=(12, 6), dpi=50)
        self.fig.autofmt_xdate()

        # create plots
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.plot(self.timearray, self.skytmphist)
        self.ax1.plot(self.timearray, self.ambtmphist)

        self.canvas = FigureCanvasTkAgg(self.fig, master=sframe)
        self.canvas.draw()
        c = self.canvas.get_tk_widget()
        c.grid(row=0, column=0)

    def __updateplot(self):
        """ Update the plot with the latest values
        """

        self.ax1.clear()
        self.ax1.plot(self.timearray, self.skytmphist)
        self.ax1.plot(self.timearray, self.ambtmphist)
        self.fig.autofmt_xdate()
        ax = self.canvas.figure.axes[0]
        maxt = max([float(a) for a in self.skytmphist + self.ambtmphist])
        mint = min([float(a) for a in self.skytmphist + self.ambtmphist])

        ax.set_ylim(int(mint) - 2, int(maxt) + 2)
        self.canvas.draw()
        c = self.canvas.get_tk_widget()
        c.grid(row=0, column=0)

    def __info(self, frame):
        """ Show the info panel.
        """
        skytemplabel = tkinter.ttk.Label(frame, text="Sky Temperature (C)")
        skytemplabel.grid(column=0, row=0, padx=5, sticky=(N, S, E, W))
        self.skytemp = tkinter.ttk.Label(frame, text="-10")
        self.skytemp.grid(column=1, row=0, padx=5, sticky=(N, S, E, W))

        ambtemplabel = tkinter.ttk.Label(frame, text="Ambient Temperature (C)")
        ambtemplabel.grid(column=0, row=1, padx=5, sticky=(N, S, E, W))
        self.ambtemp = tkinter.ttk.Label(frame, text="0")
        self.ambtemp.grid(column=1, row=1, padx=5, sticky=(N, S, E, W))

        thresholdlabel = tkinter.ttk.Label(frame, text="Threshold Temperature")
        thresholdlabel.grid(column=0, row=2, padx=5, sticky=(N, S, E, W))
        threshold = tkinter.ttk.Entry(frame, textvariable=self.threshold)
        threshold.grid(column=1, row=2, padx=5, sticky=(N, S, E, W))

        comlabel = tkinter.ttk.Label(frame, text="Select Client/Server Mode: ")
        comlabel.grid(column=0, row=3, padx=5, sticky=(N, S, E, W))
        self.com = tkinter.ttk.Combobox(frame, textvariable=self.csmode)
        self.com['values'] = ('Off', 'Client', 'Server')
        self.com.current(0)
        self.com.grid(column=1, row=3, padx=5, sticky=(N, S, E, W))

        self.mutebutton = tkinter.ttk.Button(frame, text="Mute",
                                             command=self.__mutebutton)
        self.mutebutton.grid(column=0, row=4, padx=5, sticky=(N, S, E, W))
        self.stopbutton = tkinter.ttk.Button(frame, text="Start",
                                             command=self.__stopbutton)
        self.stopbutton.grid(column=1, row=4, padx=5, sticky=(N, S, E, W))
        resetbutton = tkinter.ttk.Button(frame, text="Reset", command=self.__reset)
        resetbutton.grid(column=0, row=5, padx=5, sticky=(N, S, E, W))

    def __reset(self):
        """ Purge the existing cloud data.
        """
        self.skytmphist = []
        self.ambtmphist = []
        self.timearray = []

    def __stopbutton(self):
        """ Private function to toggle stop and start and change button text.
        """
        if self.stop is False:
            self.stop = True
            self.stopbutton.config(text='Start')
        else:
            self.stop = False
            self.stopbutton.config(text='Stop')

    def __mutebutton(self):
        """ Private function to toggle mute and change button text
        """
        if self.mute is False:
            self.mute = True
            self.mutebutton.config(text='Unmute')
        else:
            self.mute = False
            self.mutebutton.config(text='Mute')

    def updatetmp(self):
        """ Update the temperatures and gui.
            Also check if we need to raise alarm.
        """
        if self.stop:
            self.frame.after(polldelay, self.updatetmp)
            return
        if 'Client' in self.csmode.get():
            try:
                if self.socket is not None:
                    self.socket.close()
                    self.socket = None
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((socket.gethostname(), 8001))
                mesg = self.socket.recv(32).strip('\0')
                self.socket.close()
            except Exception as msg:
                log.error("client exception: " + str(msg))
            if mesg is None:
                log.warning("Didn't get a response from the server...")
                self.frame.after(polldelay, self.updatetmp)
                return
            else:
                [a, b, c] = mesg.split(';')
                self.timearray.append(datetime.datetime.strptime(a.split('.')[0], '%Y-%m-%d %H:%M:%S'))
                self.skytmphist.append(int(b))
                self.ambtmphist.append(int(c))
        else:
            log.debug("Arduino is connected? " + str(self.uno.isconnected()))
            if self.uno.isconnected() == True:
                # Add workaround for 1037.55
                newtmp, anewtmp = self.uno.get_temperatures()
                if newtmp == '1037.55':
                    try:
                        self.skytmphist.append(self.skytmphist[-1])
                    except IndexError:
                        self.skytmphist.append('0')
                else:
                    self.skytmphist.append(newtmp)
                if anewtmp == '1037.55':
                    try:
                        self.ambtmphist.append(self.ambtmphist[-1])
                    except IndexError:
                        self.ambtmphist.append('0')
                else:
                    self.ambtmphist.append(anewtmp)
                templog.debug("sky=" + str(newtmp) + ":ambient=" + str(anewtmp))

            else:
                newtmp = randint(0, 100)
                anewtmp = randint(0, 100)
                templog.debug("sky=" + str(newtmp) + ":ambient=" + str(anewtmp))
                self.skytmphist.append(newtmp)
                self.ambtmphist.append(anewtmp)
            tnow = datetime.datetime.now()
            self.timearray.append(tnow)
        self.skytemp.config(text=str(self.skytmphist[-1]))
        self.ambtemp.config(text=str(self.ambtmphist[-1]))
        self.__updateplot()
        if (float(self.skytmphist[-1]) > float((self.threshold.get()))) and not self.mute:
            log.debug("BEEEEEEEPPPPPP")
            if sys.platform == 'darwin':
                audio_file = "Siren_Noise.wav"
                subprocess.Popen(["afplay " + audio_file], shell=True,
                                 stdin=None, stdout=None, stderr=None,
                                 close_fds=True)
        self.frame.after(polldelay, self.updatetmp)

    def network(self):
        """ Either Run a tcp server that a client can connect to
            or run a client to connect to a server
            or do nothing.
        """
        mode = self.csmode.get()
        # print mode
        if 'Off' in mode:
            self.frame.after(offdelay, self.network)
            return
        elif 'Server' in mode:
            if self.socket is None:
                self.socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.socket.bind((socket.gethostname(), 8001))
                self.socket.setblocking(0)
                self.socket.listen(5)
            try:
                cstring = str(self.timearray[-1]) + ";" + \
                          str(self.skytmphist[-1]) + ";" + \
                          str(self.ambtmphist[-1]) + "\0"
                a, b, c = select.select([self.socket], [], [], 0)
                for s in a:
                    client_socket, address = self.socket.accept()
                    client_socket.send(cstring)
            except Exception as msg:
                log.error("exception1: " + str(msg))
            self.frame.after(serverdelay, self.network)


if __name__ == "__main__":
    ROOT = Tk()
    CloudSensor(ROOT)
    ROOT.title("Cloud Sensor")
    ROOT.mainloop()

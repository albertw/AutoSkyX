''' Module to implement the Arduino based cloud sensor

    Siren wav from http://soundbible.com/1577-Siren-Noise.html
'''
from Tkinter import N, S, E, W, StringVar, Tk
import datetime
from random import randint
import subprocess
import sys
import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from arduino import Arduino

try:
    import winsound
except ImportError:
    # must not be windows...
    pass


# delay in ms to update temperatures
polldelay = 2000

class CloudSensor(object):
    ''' Cloud sensor notebook object'''
    def __init__(self, frame):
        ''' initiate the window'''
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

        rframe = ttk.Frame(self.frame)
        rframe.grid(sticky=(N, S, E, W))

        plot = ttk.Frame(rframe)
        plot.grid(column=0, row=0, sticky=(N, E, W))
        plot.columnconfigure(1, weight=3)

        self.__plot(plot)

        info = ttk.Frame(rframe)
        info.grid(column=1, row=0, sticky=(N, E, W))
        info.rowconfigure(0, weight=3)

        self.__info(info)
        self.frame.after(2000, self.updatetmp)

    def __plot(self, frame):
        ''' Draw the plot of temperatures.
        '''
        sframe = ttk.Frame(frame)
        sframe.grid()
        self.fig = Figure(figsize=(12, 6), dpi=50)
        self.fig.autofmt_xdate()

        # create plots
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.plot(self.timearray, self.skytmphist)
        self.ax1.plot(self.timearray, self.ambtmphist)

        self.canvas = FigureCanvasTkAgg(self.fig, master=sframe)
        self.canvas.show()
        c = self.canvas.get_tk_widget()
        c.grid(row=0, column=0)

    def __updateplot(self):
        ''' Update the plot with the latest values
        '''

        self.ax1.clear()
        self.ax1.plot(self.timearray, self.skytmphist)
        self.ax1.plot(self.timearray, self.ambtmphist)
        self.fig.autofmt_xdate()
        ax = self.canvas.figure.axes[0]
        ax.set_ylim(0, max(max(self.skytmphist), max(self.ambtmphist)))
        self.canvas.draw()
        c = self.canvas.get_tk_widget()
        c.grid(row=0, column=0)

    def __info(self, frame):
        ''' Show the info panel.
        '''
        skytemplabel = ttk.Label(frame, text="Sky Temperature (C)")
        skytemplabel.grid(column=0, row=0, padx=5, sticky=(N, S, E, W))
        self.skytemp = ttk.Label(frame, text="-10")
        self.skytemp.grid(column=1, row=0, padx=5, sticky=(N, S, E, W))

        ambtemplabel = ttk.Label(frame, text="Ambient Temperature (C)")
        ambtemplabel.grid(column=0, row=1, padx=5, sticky=(N, S, E, W))
        self.ambtemp = ttk.Label(frame, text="0")
        self.ambtemp.grid(column=1, row=1, padx=5, sticky=(N, S, E, W))

        thresholdlabel = ttk.Label(frame, text="Threshold Temperature")
        thresholdlabel.grid(column=0, row=2, padx=5, sticky=(N, S, E, W))
        threshold = ttk.Entry(frame, textvariable=self.threshold)
        threshold.grid(column=1, row=2, padx=5, sticky=(N, S, E, W))

        warning = ttk.Label(frame, text="DEMO MODE")
        warning.grid(column=0, row=3, padx=5, sticky=(N, S, E, W))

    def updatetmp(self):
        ''' Update the temperatures and gui.
            Also check if we need to raise alarm.
        '''
        newtmp = randint(0, 100)
        anewtmp = randint(0, 100)
        #newtmp, anewtmp = uno.get_temperatures()
        self.skytmphist.append(newtmp)
        self.ambtmphist.append(anewtmp)
        self.timearray.append(datetime.datetime.now())
        self.skytemp.config(text=str(newtmp))
        self.ambtemp.config(text=str(anewtmp))
        self.__updateplot()
        if newtmp > int(self.threshold.get()):
            if sys.platform == 'darwin':
                audio_file = "Siren_Noise.wav"
                subprocess.Popen(["afplay " + audio_file], shell=True,
                                 stdin=None, stdout=None, stderr=None,
                                 close_fds=True)
        self.frame.after(polldelay, self.updatetmp)

if __name__ == "__main__":
    ROOT = Tk()
    CloudSensor(ROOT)
    ROOT.title("Cloud Sensor")
    ROOT.mainloop()

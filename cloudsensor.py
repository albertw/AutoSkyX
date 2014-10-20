''' Module to implement the Arduino based cloud sensor
'''
from Tkinter import N, S, E, W, StringVar, Tk
import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

class CloudSensor(object):
    ''' Cloud sensor notebook object'''
    def __init__(self, frame):
        ''' initiate the window'''
        self.threshold = StringVar()
        self.frame = frame

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

    def __plot(self, frame):
        ''' Draw the plot of temperatures.
        '''
        sframe = ttk.Frame(frame)
        sframe.grid()
        fig = Figure(figsize=(12, 6), dpi=50)

        # create plots
        a1 = fig.add_subplot(111)
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(2*np.pi*t)
        a1.plot(t, s)

        canvas = FigureCanvasTkAgg(fig, master=sframe)
        canvas.show()
        c = canvas.get_tk_widget()
        c.grid(row=0, column=0)

    def __info(self, frame):
        ''' Show the info panel.
        '''
        skytemplabel = ttk.Label(frame, text="Sky Temperature (C)")
        skytemplabel.grid(column=0, row=0, padx=5, sticky=(N, S, E, W))
        skytemp = ttk.Label(frame, text="-10")
        skytemp.grid(column=1, row=0, padx=5, sticky=(N, S, E, W))

        ambtemplabel = ttk.Label(frame, text="Ambient Temperature (C)")
        ambtemplabel.grid(column=0, row=1, padx=5, sticky=(N, S, E, W))
        ambtemp = ttk.Label(frame, text="0")
        ambtemp.grid(column=1, row=1, padx=5, sticky=(N, S, E, W))

        thresholdlabel = ttk.Label(frame, text="Threshold Temperature")
        thresholdlabel.grid(column=0, row=2, padx=5, sticky=(N, S, E, W))
        threshold = ttk.Entry(frame, textvariable=self.threshold)
        threshold.grid(column=1, row=2, padx=5, sticky=(N, S, E, W))

if __name__ == "__main__":
    ROOT = Tk()
    CloudSensor(ROOT)
    ROOT.title("Cloud Sensor")
    ROOT.mainloop()

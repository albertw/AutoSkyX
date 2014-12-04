''' Module to implement the Arduino based cloud sensor

    Siren wav from http://soundbible.com/1577-Siren-Noise.html
'''

from Tkinter import N, S, E, W, StringVar, Tk
import datetime
from random import randint
import subprocess
import sys
import socket
import select
import ttk

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
        self.csmode = StringVar()
        self.socket = None
        self.mute = False
        self.mutebutton = None
        self.com = None

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

        self.updatetmp()
        self.network()

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

        comlabel = ttk.Label(frame, text="Select Client/Server Mode: ")
        comlabel.grid(column=0, row=3, padx=5, sticky=(N, S, E, W))
        self.com = ttk.Combobox(frame, textvariable=self.csmode)
        self.com['values'] = ('Off', 'Client', 'Server')
        self.com.current(0)
        self.com.grid(column=1, row=3, padx=5, sticky=(N, S, E, W))

        self.mutebutton = ttk.Button(frame, text="Mute",
                                     command=self.__mutebutton)
        self.mutebutton.grid(column=0, row=4, padx=5, sticky=(N, S, E, W))

        warning = ttk.Label(frame, text="DEMO MODE")
        warning.grid(column=0, row=5, padx=5, sticky=(N, S, E, W))

    def __mutebutton(self):
        ''' Private function to toggle mute and change button text
        '''
        if self.mute == False:
            self.mute = True
            self.mutebutton.config(text='Unmute')
        else:
            self.mute = False
            self.mutebutton.config(text='Mute')

    def updatetmp(self):
        ''' Update the temperatures and gui.
            Also check if we need to raise alarm.
        '''
        if 'Client' in self.csmode.get():
            try:
                if self.socket != None:
                    self.socket.close()
                    self.socket = None
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((socket.gethostname(), 8001))
                mesg = self.socket.recv(32).strip('\0')
                self.socket.close()
            except Exception as msg:
                print ("client exception: " +  str(msg))
            if mesg == None:
                print "Didn't get a response from the server..."
                self.frame.after(polldelay, self.updatetmp)
                return
            else:
                [a, b, c] = mesg.split(';')
                self.timearray.append(datetime.datetime.strptime(a.split('.')[0], '%Y-%m-%d %H:%M:%S'))
                self.skytmphist.append(int(b))
                self.ambtmphist.append(int(c))
        else:
            if self.uno.isconnected == True:
                #newtmp, anewtmp = uno.get_temperatures()
                pass
            else:
                newtmp = randint(0, 100)
                anewtmp = randint(0, 100)
                self.skytmphist.append(newtmp)
                self.ambtmphist.append(anewtmp)
            tnow = datetime.datetime.now()
            self.timearray.append(tnow)
        self.skytemp.config(text=str(self.skytmphist[-1]))
        self.ambtemp.config(text=str(self.ambtmphist[-1]))
        self.__updateplot()
        # TODO: And a start/stop button...
        print self.mute
        if self.skytmphist[-1] > int(self.threshold.get()) and not self.mute:
            if sys.platform == 'darwin':
                audio_file = "Siren_Noise.wav"
                subprocess.Popen(["afplay " + audio_file], shell=True,
                                 stdin=None, stdout=None, stderr=None,
                                 close_fds=True)
        self.frame.after(polldelay, self.updatetmp)

    def network(self):
        ''' Either Run a tcp server that a client can connect to
            or run a client to connect to a server
            or do nothing.
        '''
        mode = self.csmode.get()
        #print mode
        if 'Off' in mode:
            self.frame.after(offdelay, self.network)
            return
        elif 'Server' in mode:
            if self.socket == None:
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
                print ("exception1: " +  str(msg))
            self.frame.after(serverdelay, self.network)

if __name__ == "__main__":
    ROOT = Tk()
    CloudSensor(ROOT)
    ROOT.title("Cloud Sensor")
    ROOT.mainloop()

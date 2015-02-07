''' AutoSkyXGUI root window module
'''
from Tkinter import N, S, E, W, Tk, FALSE, Menu
import logging
import ttk

from arduinogui import ArduinoGUI
import arduinogui
import cloudsensor
import focuser
import imagescheduler
import neocphelper


logger = logging.getLogger()

logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Set up the root window
root = Tk()
root.option_add('*tearOff', FALSE)
root.title("AutoSkyX")

# Set up Notebook tabs
n = ttk.Notebook(root)
f1 = ttk.Frame(n)
f1.grid(column=0, row=0, sticky=(N, S, E, W))
f1.columnconfigure(0, weight=3)
f1.rowconfigure(0, weight=3)
f2 = ttk.Frame(n)
f2.grid(column=0, row=0, sticky=(N, S, E, W))
f2.columnconfigure(0, weight=3)
f2.rowconfigure(0, weight=3)
f3 = ttk.Frame(n)
f3.grid(column=0, row=0, sticky=(N, S, E, W))
f3.columnconfigure(0, weight=3)
f3.rowconfigure(0, weight=3)
f4 = ttk.Frame(n)
f4.grid(column=0, row=0, sticky=(N, S, E, W))
f4.columnconfigure(0, weight=3)
f4.rowconfigure(0, weight=3)
f5 = ttk.Frame(n)
f5.grid(column=0, row=0, sticky=(N, S, E, W))
f5.columnconfigure(0, weight=3)
f5.rowconfigure(0, weight=3)
n.add(f1, text="NEOCPHelper")
n.add(f2, text="AutoSkyX")
n.add(f3, text="Focuser")
n.add(f4, text="CloudSensor")
n.add(f5, text="Arduino")

neos = neocphelper.neocp(f1)
isframe = imagescheduler.imagescheduler(f2, neos)
focuserframe = focuser.Focuser(f3)
cloudframe = cloudsensor.CloudSensor(f4)
arduinoframe = arduinogui.ArduinoGUI(f5)
# Add menubar
menubar = Menu(root)
menubar.add_cascade(label="File")
menubar.add_cascade(label="Help")

n.grid(column=0, row=0, sticky=(N, S, E, W))
n.grid_columnconfigure(0, weight=1)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.config(menu=menubar)

root.mainloop()

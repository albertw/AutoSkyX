''' AutoSkyXGUI root window module
'''
from Tkinter import N, S, E, W, Tk, FALSE, Menu
import logging
import logging.config
logging.config.fileConfig('config.ini')
logger = logging.getLogger(__name__)

import platform
import ttk
import sys

from configgui import ConfigGUI
import configgui
import cloudsensor
import imagescheduler
import focuser
import neocphelper

if (platform.architecture()[0] == '64bit' and 
    "Windows" in platform.architecture()[1]):
    logger.warning("We can't run on 64bit windows sorry")
    sys.exit(1)

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
n.add(f2, text="Image Scheduler")
n.add(f3, text="Focuser")
n.add(f4, text="CloudSensor")
n.add(f5, text="Config")

neos = neocphelper.neocp(f1)
isframe = imagescheduler.imagescheduler(f2, neos)
focuserframe = focuser.Focuser(f3)
cloudframe = cloudsensor.CloudSensor(f4)
configframe = configgui.ConfigGUI(f5)
# Add menubar
menubar = Menu(root)
menubar.add_cascade(label="File")
menubar.add_cascade(label="Help")

n.grid(column=0, row=0, sticky=(N, S, E, W))
n.grid_columnconfigure(0, weight=1)

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.config(menu=menubar)
logger.debug("Starting.")
root.mainloop()

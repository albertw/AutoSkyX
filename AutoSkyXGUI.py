""" AutoSkyXGUI root window module
"""
import logging.config
import tkinter.ttk
from tkinter import N, S, E, W, Tk, FALSE, Menu

logging.config.fileConfig('config.ini')
logger = logging.getLogger(__name__)

import cloudsensor
import configgui
import focuser
import imagescheduler
import neocphelper

"""
if (platform.architecture()[0] == '64bit' and 
    "Windows" in platform.architecture()[1]):
    logger.warning("We can't run on 64bit windows sorry")
    sys.exit(1)
"""

# Set up the root window
root = Tk()
root.option_add('*tearOff', FALSE)
root.title("AutoSkyX")

# Set up Notebook tabs
n = tkinter.ttk.Notebook(root)
f1 = tkinter.ttk.Frame(n)
f1.grid(column=0, row=0, sticky=(N, S, E, W))
f1.columnconfigure(0, weight=3)
f1.rowconfigure(0, weight=3)
f2 = tkinter.ttk.Frame(n)
f2.grid(column=0, row=0, sticky=(N, S, E, W))
f2.columnconfigure(0, weight=3)
f2.rowconfigure(0, weight=3)
f3 = tkinter.ttk.Frame(n)
f3.grid(column=0, row=0, sticky=(N, S, E, W))
f3.columnconfigure(0, weight=3)
f3.rowconfigure(0, weight=3)
f4 = tkinter.ttk.Frame(n)
f4.grid(column=0, row=0, sticky=(N, S, E, W))
f4.columnconfigure(0, weight=3)
f4.rowconfigure(0, weight=3)
f5 = tkinter.ttk.Frame(n)
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


def refresh(event):
    """ Refresh the data in the tabs.
    """
    tab = event.widget.tab('current')['text']
    if tab == "NEOCPHelper":
        neos.refresh(event)
    elif tab == "Image Scheduler":
        isframe.refresh(event)


root.bind("<<NotebookTabChanged>>", refresh)

root.mainloop()

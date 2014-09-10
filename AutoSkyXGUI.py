
from Tkinter import *
from tkFileDialog import *
import ttk

import neocphelper


    
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
n.add(f1, text="NEOCPHelper")
n.add(f2, text="AutoSkyX")

neocphelperframe=neocphelper.neocp(f1)

# Placeholder text for autoskyxtab
autoskyxcontainer = ttk.Frame(f2)
autoskyxcontainer.grid(column=0, row=0)
asx = ttk.Label(autoskyxcontainer, text="Not yet implemented")
asx.grid(column=0, row=0)

# Add menubar
menubar = Menu(root)
menubar.add_cascade(label="File")
menubar.add_cascade(label="Help")

n.grid(column=0, row=0, sticky=(N, S, E, W))
n.grid_columnconfigure(0 , weight=1)


root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.config(menu=menubar)

root.mainloop()

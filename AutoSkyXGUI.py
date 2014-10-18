''' AutoSkyXGUI root window module
'''
from Tkinter import N, S, E, W, Tk, FALSE, Menu
import imagescheduler
import neocphelper
import ttk


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

neos = neocphelper.neocp(f1)
isframe = imagescheduler.imagescheduler(f2, neos)

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

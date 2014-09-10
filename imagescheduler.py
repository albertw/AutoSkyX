
from Tkinter import *
from tkFileDialog import *
import tkFont
import ttk
import urllib2
import tkMessageBox

class imagescheduler():
    
    def __init__(self, frame, neoobj):
        self.frame = frame
        self.tree_columns = ("Target","Exposure","No. Exposures","RA","Dec","Alt","Az")

        self.tlist = []
        self.autoguide=0
        self.closedloop=1
        
        self.ttable = ttk.Frame(self.frame)
        self.tedit = ttk.Frame(self.frame)
        self.rbuttons = ttk.Frame(self.frame)
        
        self.ttable.grid(column=0, row=0, sticky=(N, S, E, W))
        self.ttable.grid_columnconfigure(0 , weight=1)
        self.ttable.columnconfigure(0, weight=3)
        self.ttable.rowconfigure(0, weight=3)
        self.tedit.grid(column=1, row=0, sticky=(N, S, E, W))        
        self.rbuttons.grid(column=2, row=0, sticky=(N, S, E, W))
        
        
        # Right Buttons
        loadbut = ttk.Button(self.rbuttons, text="Load Schedule")
        savebut = ttk.Button(self.rbuttons, text="Save Schedule")
        updateskyxbut = ttk.Button(self.rbuttons, text="Update data from skyx")
        loadNEObut = ttk.Button(self.rbuttons, text="Load selected NEOs ")
        autoguide = ttk.Checkbutton(self.rbuttons, text="Use Autoguiding", variable=self.autoguide)
        closedloop = ttk.Checkbutton(self.rbuttons, text="Use Closed Loop Slew", variable=self.closedloop)
        
        helpertext1 = "Some usage text."
        helptxt = ttk.Label(self.rbuttons, text=helpertext1, wraplength=170, anchor=W, justify=LEFT)
        
        loadbut.grid(column=0, row=0, sticky=(N, S, E, W))
        savebut.grid(column=0, row=1, sticky=(N, S, E, W))
        updateskyxbut.grid(column=0, row=2, sticky=(N, S, E, W))
        loadNEObut.grid(column=0, row=3, sticky=(N, S, E, W))
        autoguide.grid(column=0, row=4, sticky=(N, S, E, W))
        closedloop.grid(column=0, row=5, sticky=(N, S, E, W))
        helptxt.grid(column=0, row=6, sticky=(N, S, E, W), ipady=20, padx=10)
        
        # Edit
        l = ttk.Button(self.tedit,text="Save Target")
        l.grid(column=0, row=0, sticky=(N, S, E, W))

        # List
        self.ttree = ttk.Treeview(self.ttable, columns=self.tree_columns, show="headings")
        vsb = ttk.Scrollbar(orient="vertical")
        self.ttree.configure(yscrollcommand=vsb.set)
        self.ttree.grid(column=0, row=0, columnspan=5, sticky='nsew', in_=self.ttable)
        vsb.grid(column=5, row=0, sticky='ns', in_=self.ttable)
        # data is fixed width so just do it for the headings that we've already spaced out
        for col in self.tree_columns:
            self.ttree.heading(col, text=col.title(), command=lambda c=col: self.sortby(self.neocptree, c, 0))
            self.ttree.column(col, width=tkFont.Font().measure(col.title()) + 5)
        
        delrows = ttk.Button(self.ttable, text="Delete rows")
        addrows = ttk.Button(self.ttable, text="Add row")
        run = ttk.Button(self.ttable, text="Run Schedule")
        up = ttk.Button(self.ttable, text="Up")
        down = ttk.Button(self.ttable, text="Down")

        delrows.grid(column=4, row=1, sticky=(E))
        addrows.grid(column=3, row=1, sticky=(E))
        up.grid(column=2, row=1, sticky=(E))
        down.grid(column=1, row=1, sticky=(E))
        run.grid(column=0, row=1, sticky=(W))
        
        self.ttable.grid(column=0, row=0, sticky=(N, W, E, S))

    
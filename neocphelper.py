#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from Tkinter import *
from tkFileDialog import *
import tkFont
import ttk

import MPCweb
import SkyXDB
import SkyXConnection

class neocp():
    
    def __init__(self, frame):
        self.frame = frame
        self.tree_columns = ("Tmp. Desig", "Score", "    Discovery    ", "    R.A.   ",
                "    Decl.    ", "   Alt.   ", "   Az.   ", "   Angle   ",
                "   Rate   ", "    V    ", "            Updated            ",
                 "Note", "NObs", " Arc ", "   H  ")

        self.mpc = MPCweb.MPCweb()
        self.neocplist = []
        
        self.content = ttk.Frame(self.frame)
        self.bcontainer = ttk.Frame(self.frame)
        
        self.content.grid(column=0, row=0, sticky=(N, S, E, W))
        self.content.grid_columnconfigure(0 , weight=1)
        self.content.columnconfigure(0, weight=3)
        self.content.rowconfigure(0, weight=3)
        
        self.bcontainer.grid(column=1, row=0, sticky=(N, S, E, W))
        
        
        # Right Buttons
        getNeocp = ttk.Button(self.bcontainer, text="Get NEOCP", command=self.getNeocpHandler)
        saveSADB = ttk.Button(self.bcontainer, text="Save Small Asteroid db",command=self.gensmalldbHandler)
        updateskyx = ttk.Button(self.bcontainer, text="Update Alt/Az from skyx",command=self.updatefromskyxHandler)
        saveFO = ttk.Button(self.bcontainer, text="Save in findorb format")
        helpertext1 = "Click on the 'Get NEOCP' button to populate the table. Then delete unwanted rows. Next save in skyx format and load in skyx.  You can then update the Alt/Az, Rate and angle information from the skyx."
        helptxt = ttk.Label(self.bcontainer, text=helpertext1, wraplength=170, anchor=W, justify=LEFT)
        
        getNeocp.grid(column=0, row=0, sticky=(N, S, E, W))
        saveSADB.grid(column=0, row=1, sticky=(N, S, E, W))
        updateskyx.grid(column=0, row=2, sticky=(N, S, E, W))
        saveFO.grid(column=0, row=3, sticky=(N, S, E, W))
        helptxt.grid(column=0, row=4, sticky=(N, S, E, W), ipady=20, padx=10)
        
        # List
        self.neocptree = ttk.Treeview(self.content, columns=self.tree_columns, show="headings", displaycolumns=[0, 10, 3, 4, 5, 6, 7, 8, 9, 11, 12])
        vsb = ttk.Scrollbar(orient="vertical", command=self.neocptree.yview)
        self.neocptree.configure(yscrollcommand=vsb.set)
        self.neocptree.grid(column=0, row=0, sticky='nsew', in_=self.content)
        vsb.grid(column=1, row=0, sticky='ns', in_=self.content)
        # data is fixed width so just do it for the headings that we've already spaced out
        for col in self.tree_columns:
            self.neocptree.heading(col, text=col.title(), command=lambda c=col: self.sortby(self.neocptree, c, 0))
            self.neocptree.column(col, width=tkFont.Font().measure(col.title()) + 5)
        
        delrows = ttk.Button(self.content, text="Delete rows",command=self.deleteRowsHandler)
        delrows.grid(column=0, row=1, sticky=(E))
        
        self.neocptree.grid(column=0, row=0, sticky=(N, W, E, S))

    
    def getNeocpHandler(self,*args):
        for item in self.neocptree.get_children():
            self.neocptree.delete(item)
        self.neocplist = self.mpc.getneocp()
        for item in self.neocplist:
            self.neocptree.insert('', 'end', values=item.neolist())

    def sortby(self, tree, col, descending):
        """Sort tree contents when a column is clicked on."""
        # grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
    
        # reorder data
        data.sort(reverse=descending)
        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)
    
        # switch the heading so that it will sort in the opposite direction
        tree.heading(col,
            command=lambda col=col: self.sortby(tree, col, int(not descending)))
    
    def deleteRowsHandler(self, *args):
        print self.neocplist
        for item in self.neocptree.selection():
            tmpdesig = self.neocptree.item(item)['values'][0]
            self.neocplist = ([x for x in self.neocplist if x.tmpdesig != tmpdesig])
            self.neocptree.delete(item)
            
    def gensmalldbHandler(self, *args):
        smalldb = SkyXDB.genSmallDB(self.neocplist)
        filename = asksaveasfilename()
        f = open(filename, 'w')
        f.write(smalldb)
        f.close()
        
    def updatefromskyxHandler(self, *args):
        for target in self.neocplist:
            target.updateskyxinfo()
        # Repopulate the tree
        for item in self.neocptree.get_children():
            self.neocptree.delete(item)
        for item in self.neocplist:
            self.neocptree.insert('', 'end', values=item.neolist())
            

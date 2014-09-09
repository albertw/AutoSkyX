#! /usr/bin/python

# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.


import MPCweb
from Tkinter import *
from tkFileDialog import *
import ttk
import tkFont
import pprint
import SkyXDB

tree_columns = ("Tmp. Desig", "Score", "    Discovery    ", "    R.A.   ",
                "    Decl.    ", "   Alt.   ", "   Az.   ", "   Angle   ", 
                "   Rate   ", "    V    ", "            Updated            ",
                 "Note", "NObs", " Arc ", "   H  ")

mpc = MPCweb.MPCweb()
neocplist = []

def getNeocpHandler(*args):
    global neocplist
    for item in neocptree.get_children():
        neocptree.delete(item)
    neocplist=mpc.getneocp()
    for item in neocplist:
        neocptree.insert('', 'end', values=item.neolist())
    
def sortby(tree, col, descending):
    """Sort tree contents when a column is clicked on."""
    # grab values to sort
    data = [(tree.set(child, col), child) for child in tree.get_children('')]

    # reorder data
    data.sort(reverse=descending)
    for indx, item in enumerate(data):
        tree.move(item[1], '', indx)

    # switch the heading so that it will sort in the opposite direction
    tree.heading(col,
        command=lambda col=col: sortby(tree, col, int(not descending)))

def deleteRowsHandler(*args):
    global neocplist
    for item in neocptree.selection():
        tmpdesig=neocptree.item(item)['values'][0]
        neocplist=([x for x in neocplist if x.tmpdesig!=tmpdesig])
        neocptree.delete(item)
        
def gensmalldbHandler(*args):
    global neocplist
    smalldb = SkyXDB.genSmallDB(neocplist)
    filename = asksaveasfilename()
    f = open(filename,'w')
    f.write(smalldb)
    f.close()
    # launch save dialog and write this to the rsultatnt file
    
root = Tk()
root.option_add('*tearOff', FALSE)
root.title("AutoSkyX")

content = ttk.Frame(root)

menubar= Menu(content)
menubar.add_cascade(label="File")
menubar.add_cascade(label="Help")


# Right Buttons
bcontainer = ttk.Frame(root)
getNeocp = ttk.Button(bcontainer, text="Get NEOCP", command=getNeocpHandler)
saveSADB = ttk.Button(bcontainer, text="Save Small Asteroid db", command=gensmalldbHandler)
updateskyx = ttk.Button(bcontainer, text="Update Alt/Az from skyx")
saveFO = ttk.Button(bcontainer, text="Save in findorb format")
getNeocp.grid(column=0, row=0, sticky=(N, S, E, W))
saveSADB.grid(column=0, row=1, sticky=(N, S, E, W))
updateskyx.grid(column=0, row=2, sticky=(N, S, E, W))
saveFO.grid(column=0, row=3, sticky=(N, S, E, W))

# List
neocptree = ttk.Treeview(content, columns=tree_columns, show="headings",displaycolumns=[0,2,3,4,5,6,7,9,11,12])
vsb = ttk.Scrollbar(orient="vertical", command=neocptree.yview)
neocptree.configure(yscrollcommand=vsb.set)
neocptree.grid(column=0, row=0, sticky='nsew', in_=content)
vsb.grid(column=1, row=0, sticky='ns', in_=content)
        
# data is fixed width so just do it for the headings that we've already spaced out
for col in tree_columns:
    neocptree.heading(col, text=col.title(), command=lambda c=col: sortby(neocptree, c, 0))
    neocptree.column(col, width=tkFont.Font().measure(col.title()) + 5)

delrows = ttk.Button(content, text="Delete rows", command=deleteRowsHandler)

# Placing
delrows.grid(column=0, row=1, sticky=(E))

content.grid(column=0, row=0, sticky=(N, S, E, W))
content.grid_columnconfigure(0 , weight=1)
bcontainer.grid(column=1, row=0, sticky=(N, S, E, W))

neocptree.grid(column=0, row=0, sticky=(N, W, E, S))


root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

content.columnconfigure(0, weight=3)
content.rowconfigure(0, weight=3)
root.config(menu=menubar)

root.mainloop()

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
    neocplist = mpc.getneocp()
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
        tmpdesig = neocptree.item(item)['values'][0]
        neocplist = ([x for x in neocplist if x.tmpdesig != tmpdesig])
        neocptree.delete(item)
        
def gensmalldbHandler(*args):
    global neocplist
    smalldb = SkyXDB.genSmallDB(neocplist)
    filename = asksaveasfilename()
    f = open(filename, 'w')
    f.write(smalldb)
    f.close()
    
def updatefromskyxHandler(*args):
    global neocplist
    # I dont like this really. should probably be more like:
    # target.updateskyxinfo() - let the class do the work.
    skyx = SkyXConnection.SkyXConnection()
    for target in neocplist:
        skyxinfo=skyx.sky6ObjectInformation(target.tmpdesig)
        target.az=skyxinfo['sk6ObjInfoProp_AZM']
        target.alt=skyxinfo['sk6ObjInfoProp_ALT']
        target.ra=skyxinfo['sk6ObjInfoProp_RA_2000']
        target.dec=skyxinfo['sk6ObjInfoProp_DEC_2000']
    # Repopulate the tree
    for item in neocptree.get_children():
        neocptree.delete(item)
    for item in neocplist:
        neocptree.insert('', 'end', values=item.neolist())
        
    
    
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
content = ttk.Frame(f1)
bcontainer = ttk.Frame(f1)

content.grid(column=0, row=0, sticky=(N, S, E, W))
content.grid_columnconfigure(0 , weight=1)
content.columnconfigure(0, weight=3)
content.rowconfigure(0, weight=3)

bcontainer.grid(column=1, row=0, sticky=(N, S, E, W))


# Add menubar
menubar = Menu(root)
menubar.add_cascade(label="File")
menubar.add_cascade(label="Help")

# Placeholder text for autoskyxtab
autoskyxcontainer = ttk.Frame(f2)
autoskyxcontainer.grid(column=0, row=0)
asx = ttk.Label(autoskyxcontainer, text="Not yet implemented")
asx.grid(column=0, row=0)

# Right Buttons
getNeocp = ttk.Button(bcontainer, text="Get NEOCP", command=getNeocpHandler)
saveSADB = ttk.Button(bcontainer, text="Save Small Asteroid db", command=gensmalldbHandler)
updateskyx = ttk.Button(bcontainer, text="Update Alt/Az from skyx", command=updatefromskyxHandler)
saveFO = ttk.Button(bcontainer, text="Save in findorb format")
helpertext1 = "Click on the 'Get NEOCP' button to populate the table. Then delete unwanted rows. Next save in skyx format and load in skyx.  You can then update the Alt/Az, Rate and angle information from the skyx."
helptxt = ttk.Label(bcontainer, text=helpertext1, wraplength=170, anchor=W, justify=LEFT)

getNeocp.grid(column=0, row=0, sticky=(N, S, E, W))
saveSADB.grid(column=0, row=1, sticky=(N, S, E, W))
updateskyx.grid(column=0, row=2, sticky=(N, S, E, W))
saveFO.grid(column=0, row=3, sticky=(N, S, E, W))
helptxt.grid(column=0, row=4, sticky=(N, S, E, W), ipady=20, padx=10)

# List
neocptree = ttk.Treeview(content, columns=tree_columns, show="headings", displaycolumns=[0, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12])
vsb = ttk.Scrollbar(orient="vertical", command=neocptree.yview)
neocptree.configure(yscrollcommand=vsb.set)
neocptree.grid(column=0, row=0, sticky='nsew', in_=content)
vsb.grid(column=1, row=0, sticky='ns', in_=content)
# data is fixed width so just do it for the headings that we've already spaced out
for col in tree_columns:
    neocptree.heading(col, text=col.title(), command=lambda c=col: sortby(neocptree, c, 0))
    neocptree.column(col, width=tkFont.Font().measure(col.title()) + 5)

delrows = ttk.Button(content, text="Delete rows", command=deleteRowsHandler)
delrows.grid(column=0, row=1, sticky=(E))

n.grid(column=0, row=0, sticky=(N, S, E, W))
n.grid_columnconfigure(0 , weight=1)

neocptree.grid(column=0, row=0, sticky=(N, W, E, S))

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.config(menu=menubar)

root.mainloop()

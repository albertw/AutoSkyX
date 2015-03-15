''' Module for neocp help notebook
'''

from Tkinter import StringVar, N, S, E, W, LEFT
import datetime
import logging
import time
from tkFileDialog import asksaveasfilename
import tkFont
import tkMessageBox
import ttk
import urllib2

import ephem

import MPCweb

log = logging.getLogger(__name__)


class neocp(object):
    ''' Class for the neocp helper notebook
    '''

    def __init__(self, frame):
        self.frame = frame
        self.tree_columns = ("      Designation      ", "Score",
                             "    Discovery    ", "      R.A.     ",
                             "     Decl.     ", "   Alt.   ", "   Az.   ",
                             "   Angle   ", "   Rate   ", "    V    ",
                             "            Updated            ", "Note", "NObs",
                             " Arc ", "   H  ")
        self.neocplist = []
        self.smalldb = None
        self.timestring = StringVar()

        self.content = ttk.Frame(self.frame)
        self.bcontainer = ttk.Frame(self.frame)

        self.content.grid(column=0, row=0, sticky=(N, S, E, W))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=3)
        self.content.rowconfigure(0, weight=3)

        self.bcontainer.grid(column=1, row=0, sticky=(N, S, E, W))

        # Right Buttons
        getNeocp = ttk.Button(self.bcontainer, text="Get NEOCP",
                              command=self.getNeocpHandler)
        getCrits = ttk.Button(self.bcontainer, text="Get Critical List",
                              command=self.getCritsHandler)
        getOrbData = ttk.Button(self.bcontainer,
                                text="Download Orbit information",
                                command=self.getOrbDataHandler)
        saveSADB = ttk.Button(self.bcontainer,
                              text="Save Small Asteroid db",
                              command=self.gensmalldbHandler)
        updateskyx = ttk.Button(self.bcontainer,
                                text="Update Positions",
                                command=self.updatepositionsHandler)
        saveFO = ttk.Button(self.bcontainer,
                            text="Save in findorb format",
                            command=self.genfodbHandler)
        helpertext1 = "Click on the 'Get NEOCP' button to populate the " +\
            "table. Then delete unwanted rows. Next save in skyx format " +\
            "and load in skyx.  You can then update the Alt/Az, Rate and " +\
            "angle information from the skyx."
        helptxt = ttk.Label(self.bcontainer, text=helpertext1, wraplength=170,
                            anchor=W, justify=LEFT)

        getNeocp.grid(column=0, row=0, sticky=(N, S, E, W))
        getCrits.grid(column=0, row=1, sticky=(N, S, E, W))
        getOrbData.grid(column=0, row=2, sticky=(N, S, E, W))
        saveSADB.grid(column=0, row=3, sticky=(N, S, E, W))
        updateskyx.grid(column=0, row=4, sticky=(N, S, E, W))
        saveFO.grid(column=0, row=5, sticky=(N, S, E, W))
        helptxt.grid(column=0, row=6, sticky=(N, S, E, W), ipady=20, padx=10)

        # List
        self.neocptree = ttk.Treeview(self.content, columns=self.tree_columns,
                                      show="headings",
                                      displaycolumns=[0, 10, 3, 4, 5, 6, 7, 8,
                                                      9, 11, 12])
        vsb = ttk.Scrollbar(orient="vertical", command=self.neocptree.yview)
        self.neocptree.configure(yscrollcommand=vsb.set)
        self.neocptree.grid(columnspan=4, column=0, row=0,
                            sticky='nsew', in_=self.content)
        vsb.grid(column=4, row=0, sticky='ns', in_=self.content)
        # data is fixed width so just do it for the headings that
        # we've already spaced out
        for col in self.tree_columns:
            self.neocptree.heading(col, text=col.title(),
                                   command=lambda c=col: self.sortby(
                                        self.neocptree, c, 0))
            self.neocptree.column(col,
                                  width=tkFont.Font().measure(col.title()) + 5)

        timelabel = ttk.Label(self.content, text='Date and Time (UTC):')
        timelabel.grid(column=0, row=1, sticky=(E))
        now = datetime.datetime.fromtimestamp(round(time.time()))
        self.timestring.set(now.isoformat().replace('T', ' '))
        timeentry = ttk.Entry(self.content, textvariable=self.timestring)
        timeentry.grid(column=1, row=1, sticky=(E))

        delrows = ttk.Button(self.content, text="Delete rows",
                             command=self.deleteRowsHandler)
        delrows.grid(column=2, row=1, sticky=(E))
        delall = ttk.Button(self.content, text="Delete all",
                            command=self.deleteAllHandler)
        delall.grid(column=3, row=1, sticky=(E))
        self.neocptree.grid(column=0, row=0, sticky=(N, W, E, S))

    def getNeocpHandler(self):
        ''' Handler to download the list of objects from the NEOCP and display
            them in the list.
        '''
        # logging.debug("Downloading NEO data.")
        log.debug("Downloading NEO data.")
        try:
            mpc = MPCweb.MPCweb()
            self.neocplist.extend(mpc.get_neocp())
            self.neocplist = remove_dups(self.neocplist)
            for item in self.neocptree.get_children():
                self.neocptree.delete(item)
            for item in self.neocplist:
                self.neocptree.insert('', 'end', values=item.neolist())
        except urllib2.URLError, errmsg:
            mesg = "Can't get NEOCP data:\n" + str(errmsg) +\
                   "\n Check you are online."
            log.error(mesg)
            tkMessageBox.showinfo("NEOCP Error", mesg)

    def getCritsHandler(self):
        ''' Handler to get the Critical list.
        '''
        try:
            mpc = MPCweb.MPCweb()
            crits = mpc.get_crits()
            for target in crits:
                target.updateephem(self.timestring.get())
            self.neocplist.extend(crits)
            self.neocplist = remove_dups(self.neocplist)
            for item in self.neocptree.get_children():
                self.neocptree.delete(item)
            for item in self.neocplist:
                self.neocptree.insert('', 'end', values=item.neolist())
        except urllib2.URLError, errmsg:
            mesg = "Can't get Critlist data:\n" + str(errmsg) +\
                   "\n Check you are online."
            log.error(mesg)
            tkMessageBox.showinfo("Critlist Error", mesg)

    def sortby(self, tree, col, descending):
        """Sort tree contents when a column is clicked on."""
        # grab values to sort
        data = [(tree.set(child, col), child)
                for child in tree.get_children('')]

        # reorder data
        data.sort(reverse=descending)
        for indx, item in enumerate(data):
            tree.move(item[1], '', indx)

        # switch the heading so that it will sort in the opposite direction
        tree.heading(col,
                     command=lambda col=col: self.sortby(tree,
                                                         col,
                                                         int(not descending)))

    def deleteRowsHandler(self):
        ''' Handler to delete selected rows.
        '''
        for item in self.neocptree.selection():
            tmpdesig = self.neocptree.item(item)['values'][0]
            self.neocplist = ([x for x in self.neocplist
                               if x.tmpdesig != tmpdesig])
            self.neocptree.delete(item)

    def deleteAllHandler(self):
        ''' Clear the list'''
        for item in self.neocptree.get_children():
            self.neocptree.delete(item)
        self.neocplist = []

    def getOrbDataHandler(self):
        ''' Handler to download the MPC orbit information from the MPC for all
            targets.
        '''
        try:
            mpc = MPCweb.MPCweb()
            self.smalldb = mpc.gen_smalldb(self.neocplist)
        except urllib2.URLError, errmsg:
            mesg = "Can't get orbit data:\n" + str(errmsg) +\
                   "\n Check you are online."
            log.error(mesg)
            tkMessageBox.showinfo("MPC Error", mesg)

    def gensmalldbHandler(self):
        ''' Generate and save the small asteroid database for TheSkyX.
            TODO: Check this still works correctly as we delete/add objects
        '''
        try:
            if self.smalldb is None:
                log.debug("creating smalldb")
                mpc = MPCweb.MPCweb()
                self.smalldb = mpc.gen_smalldb(self.neocplist)
            filename = asksaveasfilename()
            smdbf = open(filename, 'w')
            log.debug("writing to: " + str(filename))
            log.debug("smalldb: " + str(self.smalldb))
            smdbf.write(self.smalldb)
            smdbf.close()
        except urllib2.URLError, errmsg:
            mesg = "Can't get orbit data:\n" + str(errmsg) +\
                   "\n Check you are online."
            log.error(mesg)
            tkMessageBox.showinfo("MPC Error", mesg)

    def genfodbHandler(self):
        ''' Handler to save the targets in findorb format.
        '''
        try:
            mpc = MPCweb.MPCweb()
            fodb = mpc.gen_findorb(self.neocplist)
            filename = asksaveasfilename()
            fof = open(filename, 'w')
            fof.write(fodb)
            fof.close()
        except urllib2.URLError, errmsg:
            mesg = "Can't get observations data:\n" + str(errmsg) +\
                   "\n Check you are online."
            log.error(mesg)
            tkMessageBox.showerror("MPC Error", mesg)

    def updatepositionsHandler(self):
        ''' Handler to update the positions of the targets for the selected
            time. Downloading orbit data if necessary.
        '''
        try:
            ephem.Date(self.timestring.get())
        except ValueError:
            mesg = "Please enter the Date and time in the correct format."
            log.error(mesg)
            tkMessageBox.showerror(title="Date Error", message=mesg)
            return
        mpc = MPCweb.MPCweb()
        self.smalldb = mpc.gen_smalldb(self.neocplist)
        for target in self.neocplist:
            # target.updateskyxinfo()
            # TODO we should only get the new data on a per object level
            target.updateephem(self.timestring.get())
        # Repopulate the tree
        for item in self.neocptree.get_children():
            self.neocptree.delete(item)
        for item in self.neocplist:
            self.neocptree.insert('', 'end', values=item.neolist())


def remove_dups(mplist):
    newlist = []
    mps = []
    for item in mplist:
        if item.tmpdesig not in mps:
            newlist.append(item)
            mps.append(item.tmpdesig)
    return newlist

from tkinter import N, S, E, W, LEFT, Variable
from tkinter.filedialog import asksaveasfilename, askopenfile
import json
import logging
import math
import tkinter.font
import tkinter.messagebox
import tkinter.ttk
import datetime
import time
import sys

import ephem
import target
import skyx

import MPCweb
from skyx import SkyxObjectNotFoundError, SkyxConnectionError, SkyXConnection, sky6ObjectInformation


log = logging.getLogger(__name__)


class imagescheduler(object):

    def __init__(self, frame, neoobj):

        self.frame = frame
        self.neoobj = neoobj

        # Edit pane variables
        self.tname = Variable()
        self.texposure = Variable()
        self.tnumexp = Variable()
        self.exposuree = tkinter.ttk.Entry()
        self.nexposuree = tkinter.ttk.Entry()
        self.namee = tkinter.ttk.Entry()

        self.autoguide = Variable()

        self.inittableframe()
        self.initeditframe()
        self.initrightframe()

    def inittableframe(self):
        self.tree_columns = ("    Target    ", "Exp (s)", "# Exp",
                             "     RA     ", "     Dec     ", "     Alt     ",
                             "     Az     ")

        self.tlist = []
        self.ttable = tkinter.ttk.Frame(self.frame)

        self.ttable.grid(column=0, row=0, sticky=(N, S, E, W))
        self.ttable.grid_columnconfigure(0, weight=1)
        self.ttable.columnconfigure(0, weight=3)
        self.ttable.rowconfigure(0, weight=3)

        # List
        self.ttree = tkinter.ttk.Treeview(self.ttable, columns=self.tree_columns,
                                  show="headings")
        vsb = tkinter.ttk.Scrollbar(orient="vertical")
        self.ttree.configure(yscrollcommand=vsb.set)
        self.ttree.grid(column=0, row=0, columnspan=7, sticky='nsew',
                        in_=self.ttable)
        vsb.grid(column=7, row=0, sticky='ns', in_=self.ttable)
        # data is fixed width so just do it for the headings that we've
        # already spaced out
        for col in self.tree_columns:
            self.ttree.heading(col, text=col.title(),
                                   command=lambda c=col: self.sortby(
                                        self.ttree, c, 0))
            self.ttree.column(col,
                              width=tkinter.font.Font().measure(col.title()) + 5)
        delrows = tkinter.ttk.Button(self.ttable, text="Delete rows",
                             command=self._deleteHandler)
        editrow = tkinter.ttk.Button(self.ttable, text="Edit row",
                             command=self._editrowHandler)
        run = tkinter.ttk.Button(self.ttable, text="Run Schedule",
                         command=self._runHandler)
        check = tkinter.ttk.Button(self.ttable, text="Check Schedule",
                           command=self._checkHandler)
        up = tkinter.ttk.Button(self.ttable, text="Up", command=self._up)
        down = tkinter.ttk.Button(self.ttable, text="Down", command=self._down)

        delrows.grid(column=6, row=1, sticky=(E))
        editrow.grid(column=4, row=1, sticky=(E))
        up.grid(column=3, row=1, sticky=(E))
        down.grid(column=2, row=1, sticky=(E))
        check.grid(column=1, row=1, sticky=(W))
        run.grid(column=0, row=1, sticky=(W))

        self.ttable.grid(column=0, row=0, sticky=(N, W, E, S))

    def initeditframe(self):
        self.tedit = tkinter.ttk.Frame(self.frame)
        self.tedit.grid(column=1, row=0, sticky=(S, N))

        nl = tkinter.ttk.Label(self.tedit, text="Target:")
        nl.grid(column=0, row=0, sticky=(N, S, E, W))
        self.namee = tkinter.ttk.Entry(self.tedit, textvariable=self.tname)
        self.namee.grid(column=1, row=0, sticky=(N, S, E, W))

        el = tkinter.ttk.Label(self.tedit, text="Exposure Length:")
        el.grid(column=0, row=1, sticky=(N, S, E, W))
        self.exposuree = tkinter.ttk.Entry(self.tedit, textvariable=self.texposure)
        self.exposuree.grid(column=1, row=1, sticky=(N, S, E, W))

        nel = tkinter.ttk.Label(self.tedit, text="Number of Exposures:")
        nel.grid(column=0, row=2, sticky=(N, S, E, W))
        self.nexposuree = tkinter.ttk.Entry(self.tedit, textvariable=self.tnumexp)
        self.nexposuree.grid(column=1, row=2, sticky=(N, S, E, W))

        c = tkinter.ttk.Button(self.tedit, text="Clear", command=self._clear)
        l = tkinter.ttk.Button(self.tedit, text="Save/Add Target",
                       command=self._savetargetHandler)
        c.grid(column=0, row=5, sticky=(S))
        l.grid(column=1, row=5, sticky=(S))

    def initrightframe(self):

        self.rbuttons = tkinter.ttk.Frame(self.frame)
        self.rbuttons.grid(column=2, row=0, sticky=(N, S, E, W))

        loadbut = tkinter.ttk.Button(self.rbuttons, text="Load Schedule",
                             command=self._loadsched)
        #loadbut.state(['disabled'])
        savebut = tkinter.ttk.Button(self.rbuttons, text="Save Schedule",
                             command=self._savesched)
        #savebut.state(['disabled'])
        updateskyxbut = tkinter.ttk.Button(self.rbuttons, text="Update positions",
                                   command=self._updatePositionHandler)
        # updateskyxbut.state(['disabled'])
        loadNEObut = tkinter.ttk.Button(self.rbuttons,
                                text="Add selected Minor Planets",
                                command=self._addneoHandler)
        autoguide = tkinter.ttk.Checkbutton(self.rbuttons, text="Use Autoguiding",
                                    variable=self.autoguide)
        agcal = tkinter.ttk.Button(self.rbuttons,
                                text="Calibrate Autoguider",
                                command=self._agcal)

        loadbut.grid(column=0, row=0, sticky=(N, S, E, W))
        savebut.grid(column=0, row=1, sticky=(N, S, E, W))
        updateskyxbut.grid(column=0, row=2, sticky=(N, S, E, W))
        loadNEObut.grid(column=0, row=3, sticky=(N, S, E, W))
        autoguide.grid(column=0, row=4, sticky=(N, S, E, W))
        agcal.grid(column=0, row=5, sticky=(N, S, E, W))

    def _savesched(self, *args):
        ''' save the schedule'''
        filename = asksaveasfilename()
        fof = open(filename, 'w')
        for target in self.neoobj.neocplist:
            fof.write(json.dumps(target.__dict__) + "\n")
        fof.close()
            
    def _loadsched(self, *args):
        ''' load a saved schedule '''
        fn = askopenfile()
        self.neoobj.neocplist = []
        for line in fn:
            # TODO Handle more than fixed objects
            targetj = json.loads(line)
            if targetj['ttype'] != "neo" and targetj['ttype'] != "mp":
                target=minorplanet.minorplanet(targetj['tmpdesig'], ra=targetj['ra'], dec=targetj['dec'])
                self.neoobj.neocplist.append(target) 
            else:
                log.debug("Discarding " + targetj['tmpdesig'])
        self._updatepositions()
        
    def _savetargetHandler(self, *args):
        ''' need to validate the target name - off to skyx and be sure it
        exists, check the values are sane in the other fields then add to
        the list.
        '''
        if self.tname.get() and self.texposure.get() and self.tnumexp.get():
            # If it already exists delete it
            # Really should work out how to edit it in place to not screw
            # up the order
            index = 'end'
            for item in self.ttree.get_children():
                if self.ttree.item(item)['values'][0] == self.tname.get():
                    index = self.ttree.index(item)
                    self.ttree.delete(item)
            try:
                t = [x for x in self.neoobj.neocplist if x.tmpdesig == self.tname.get()][0]
                t.exposure = self.texposure.get()
                t.nexposures = self.tnumexp.get()
                self.ttree.insert('', index, values=t.imglist())
            except IndexError:
                # It wasn't on the list
                mp = target.target(self.tname.get(), ttype="fixed", nexposures=self.tnumexp.get(), exposure=self.texposure.get())
                self.neoobj.neocplist.append(mp)
                self.ttree.insert('', index, values=mp.imglist())
                
        else:
            tkinter.messagebox.showinfo(message="Invalid Data Supplied")
        self._clear()

    def _addneoHandler(self, *args):
        for neo in self.neoobj.neocplist:
            neo.exposure = 30
            neo.nexposures = 10
            self.ttree.insert('', 'end', values=[neo.tmpdesig, neo.exposure, neo.nexposures,
                                                 neo.ra, neo.dec,
                                                 neo.alt, neo.az])

    def _editrowHandler(self, *args):
        item = self.ttree.selection()[0]
        self.namee.delete(0, 'end')
        self.namee.insert(0, self.ttree.item(item)['values'][0])
        self.exposuree.delete(0, 'end')
        self.exposuree.insert(0, self.ttree.item(item)['values'][1])
        self.nexposuree.delete(0, 'end')
        self.nexposuree.insert(0, self.ttree.item(item)['values'][2])

    def _clear(self, *args):
        self.namee.delete(0, 'end')
        self.exposuree.delete(0, 'end')
        self.nexposuree.delete(0, 'end')

    def _up(self, *args):
        for item in self.ttree.selection():
            index = self.ttree.index(item)
            self.ttree.move(item, '', index - 1)

    def _down(self, *args):
        for item in reversed(self.ttree.selection()):
            index = self.ttree.index(item)
            self.ttree.move(item, '', index + 1)

    def _deleteHandler(self, *args):
        for item in self.ttree.selection():
            tmpdesig = self.ttree.item(item)['values'][0]
            self.neoobj.neocplist = ([x for x in self.neoobj.neocplist
                               if x.tmpdesig != tmpdesig])
            self.ttree.delete(item)
            

    def _runHandler(self):
        fails =  self._check()
        if fails:
            log.debug(fails)
            tkinter.messagebox.showinfo(message=fails)
            return
        skyx = SkyXConnection()
        skyxobj = sky6ObjectInformation()
        for target in self.ttree.get_children():
            tname = self.ttree.item(target)['values'][0]
            texp = self.ttree.item(target)['values'][1]
            tnum = self.ttree.item(target)['values'][2]
            ra = self.ttree.item(target)['values'][3]
            dec = self.ttree.item(target)['values'][4]
            log.info("Starting Imagining run for " + tname)
            try:
                # TODO fix this
                skyxobj.find(ra + "," + dec)
                target_pos = skyxobj.currentTargetRaDec(j="now")
                log.info("coordinates acquired. Starting Closed Loop Slew")
                skyx.closedloopslew(target=ra + "," + dec)
                log.info("slew complete. Syncing scope position to target")
                scope.sync(target_pos)
                log.info("Synced. Starting Imagining")
                skyx.takeimages(texp, tnum)
                log.info("All images completed.")
            except SkyxConnectionError as e:
                tkinter.messagebox.showinfo(message=e)
                break
            
    def _checkHandler(self):
        try:
            fails = self._check()
        except TypeError as e:
            tkinter.messagebox.showinfo(message="Can't get target data. " + str(e))
            return (False)
        if fails:
            log.debug(fails)
            tkinter.messagebox.showinfo(message=fails)
        else:
            tkinter.messagebox.showinfo(message="All targets OK")
            return (True)

    def _agcal(self):
        ''' Call TheSkyX autoguider calibration routine
        '''
        pass
    
    def _check(self):
        ''' Simple check to see that the altitude of the targets is >10 deg
        '''
        self._updatepositions()
        msg = ""
        for target in self.ttree.get_children():
            log.debug(self.ttree.item(target)['values'])
            tname = self.ttree.item(target)['values'][0]
            alt = self.ttree.item(target)['values'][5]
            ra = self.ttree.item(target)['values'][3]
            if float(alt) < 10:
                msg = msg + self.ttree.item(target)['values'][0] + "- below horizon\n"           
            elif ra == None:
                msg = msg + self.ttree.item(target)['values'][0] + "- no RA\n"           
        return(msg)
        

    def _updatePositionHandler(self, *args):
        ''' Update the positions of our Minor Planets and if necessary from
            SkyX.'''
        # TODO a lot of this class assumes that the object is in SkyX. It wont
        # always be as we dont have an API to add objects so we'll just tell
        # skyx the ra and ded
        self._updatepositions()

    def _updatepositions(self):
        
        for target in self.neoobj.neocplist:
            # target.updateskyxinfo()
            # TODO we should only get the new data on a per object level
            # TODO call to SkyX to get coords of fixed objects if ttype and ra/dec == None
            try:
                target.updateephem()
            except Exception as e:
                tkinter.messagebox.showinfo("Skyx Error", e)

            '''
            if target.ttype != None:
                target.updateephem()
            else:
                if target.ra == None:
                    try:
                        conn = skyx.SkyXConnection('192.168.192.44')
                        obj = skyx.sky6ObjectInformation()
                        
                        try:
                            # TODO this should be in minorplanet
                            # TODO minorplanet should be renamed to target
                            conn.find(target.tmpdesig)
                            pos = obj.currentTargetRaDec(j="2000")
                            t = ephem.FixedBody()
                            t._ra = rafloat2rahours(float(pos[0]))
                            t._dec = math.radians(float(pos[1]))
                            target.ra = t._ra
                            target.dec = t._dec
                            z72 = ephem.Observer()
                            z72.lon = "-6.1136"
                            z72.lat = "53.2744"
                            z72.elevation = 100
                            z72.date = ephem.Date(datetime.datetime.fromtimestamp(round(time.time())))
                            z72.epoch = "2000"
                            t.compute(z72)
                            # Bug these are wrong
                            target.alt = t.alt
                            target.az = t.az
                        except SkyxObjectNotFoundError as e:
                            log.error(e)
                    except SkyxConnectionError as e:
                        log.error(e)
        '''
        # Repopulate the tree
        for item in self.ttree.get_children():
            self.ttree.delete(item)
        for item in self.neoobj.neocplist:
            self.ttree.insert('', 'end', values=item.imglist())

        return
    
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
        
    def _updateskyx(self, target):
        skyx = SkyXConnection()
        info = skyx.sky6ObjectInformation(target)
        return(info['sk6ObjInfoProp_RA_2000'], info['sk6ObjInfoProp_DEC_2000'],
               info['sk6ObjInfoProp_ALT'], info['sk6ObjInfoProp_AZM'])

def rafloat2rahours(f):
    m,h =  math.modf(f)
    s,m = math.modf(m*60)
    s = math.modf(s*60)[1]
    return (str(int(h)) + ":" + str(int(m)) + ":" + str((s)))

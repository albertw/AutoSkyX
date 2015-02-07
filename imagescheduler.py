from Tkinter import N, S, E, W, LEFT, Variable
import tkFont
import tkMessageBox
import ttk

import MPCweb
from SkyXConnection import SkyxObjectNotFoundError, SkyxConnectionError, SkyXConnection


class imagescheduler(object):

    def __init__(self, frame, neoobj):

        self.frame = frame
        self.neoobj = neoobj

        # Edit pane variables
        self.tname = Variable()
        self.texposure = Variable()
        self.tnumexp = Variable()
        self.exposuree = ttk.Entry()
        self.nexposuree = ttk.Entry()
        self.namee = ttk.Entry()

        self.autoguide = Variable()
        self.closedloop = Variable()

        self.inittableframe()
        self.initeditframe()
        self.initrightframe()

    def inittableframe(self):
        self.tree_columns = ("    Target    ", "Exp (s)", "# Exp",
                             "     RA     ", "     Dec     ", "     Alt     ",
                             "     Az     ")

        self.tlist = []
        self.ttable = ttk.Frame(self.frame)

        self.ttable.grid(column=0, row=0, sticky=(N, S, E, W))
        self.ttable.grid_columnconfigure(0, weight=1)
        self.ttable.columnconfigure(0, weight=3)
        self.ttable.rowconfigure(0, weight=3)


        # List
        self.ttree = ttk.Treeview(self.ttable, columns=self.tree_columns,
                                  show="headings")
        vsb = ttk.Scrollbar(orient="vertical")
        self.ttree.configure(yscrollcommand=vsb.set)
        self.ttree.grid(column=0, row=0, columnspan=7, sticky='nsew',
                        in_=self.ttable)
        vsb.grid(column=7, row=0, sticky='ns', in_=self.ttable)
        # data is fixed width so just do it for the headings that we've
        # already spaced out
        for col in self.tree_columns:
            self.ttree.heading(col, text=col.title())
            self.ttree.column(col, width=tkFont.Font().measure(col.title()) + 5)

        delrows = ttk.Button(self.ttable, text="Delete rows",
                             command=self._deleteHandler)
        editrow = ttk.Button(self.ttable, text="Edit row",
                             command=self._editrowHandler)
        run = ttk.Button(self.ttable, text="Run Schedule",
                         command=self._runHandler)
        check = ttk.Button(self.ttable, text="Check Schedule",
                           command=self._checkHandler)
        up = ttk.Button(self.ttable, text="Up", command=self._up)
        down = ttk.Button(self.ttable, text="Down", command=self._down)

        delrows.grid(column=6, row=1, sticky=(E))
        editrow.grid(column=4, row=1, sticky=(E))
        up.grid(column=3, row=1, sticky=(E))
        down.grid(column=2, row=1, sticky=(E))
        check.grid(column=1, row=1, sticky=(W))
        run.grid(column=0, row=1, sticky=(W))

        self.ttable.grid(column=0, row=0, sticky=(N, W, E, S))

    def initeditframe(self):
        self.tedit = ttk.Frame(self.frame)
        self.tedit.grid(column=1, row=0, sticky=(S, N))

        nl = ttk.Label(self.tedit, text="Target:")
        nl.grid(column=0, row=0, sticky=(N, S, E, W))
        self.namee = ttk.Entry(self.tedit, textvariable=self.tname)
        self.namee.grid(column=1, row=0, sticky=(N, S, E, W))

        el = ttk.Label(self.tedit, text="Exposure Length:")
        el.grid(column=0, row=1, sticky=(N, S, E, W))
        self.exposuree = ttk.Entry(self.tedit, textvariable=self.texposure)
        self.exposuree.grid(column=1, row=1, sticky=(N, S, E, W))

        nel = ttk.Label(self.tedit, text="Number of Exposures:")
        nel.grid(column=0, row=2, sticky=(N, S, E, W))
        self.nexposuree = ttk.Entry(self.tedit, textvariable=self.tnumexp)
        self.nexposuree.grid(column=1, row=2, sticky=(N, S, E, W))

        c = ttk.Button(self.tedit, text="Clear", command=self._clear)
        l = ttk.Button(self.tedit, text="Save/Add Target",
                       command=self._savetargetHandler)
        c.grid(column=0, row=5, sticky=(S))
        l.grid(column=1, row=5, sticky=(S))

    def initrightframe(self):

        self.rbuttons = ttk.Frame(self.frame)
        self.rbuttons.grid(column=2, row=0, sticky=(N, S, E, W))

        loadbut = ttk.Button(self.rbuttons, text="Load Schedule")
        loadbut.state(['disabled'])
        savebut = ttk.Button(self.rbuttons, text="Save Schedule")
        savebut.state(['disabled'])
        updateskyxbut = ttk.Button(self.rbuttons, text="Update positions",
                                   command=self._updatePositionHandler)
        # updateskyxbut.state(['disabled'])
        loadNEObut = ttk.Button(self.rbuttons, 
                                text="Add selected Minor Planets",
                                command=self._addneoHandler)
        autoguide = ttk.Checkbutton(self.rbuttons, text="Use Autoguiding",
                                    variable=self.autoguide)
        autoguide.state(['disabled'])
        closedloop = ttk.Checkbutton(self.rbuttons, text="Use Closed Loop Slew",
                                     variable=self.closedloop)
        closedloop.state(['disabled'])

        helpertext1 = "SAll NEO's need to be in TheSkyX before running."
        helptxt = ttk.Label(self.rbuttons, text=helpertext1, wraplength=170,
                            anchor=W, justify=LEFT)

        loadbut.grid(column=0, row=0, sticky=(N, S, E, W))
        savebut.grid(column=0, row=1, sticky=(N, S, E, W))
        updateskyxbut.grid(column=0, row=2, sticky=(N, S, E, W))
        loadNEObut.grid(column=0, row=3, sticky=(N, S, E, W))
        autoguide.grid(column=0, row=4, sticky=(N, S, E, W))
        closedloop.grid(column=0, row=5, sticky=(N, S, E, W))
        helptxt.grid(column=0, row=6, sticky=(N, S, E, W), ipady=20, padx=10)

    def _savetargetHandler(self, *args):
        ''' need to validate the target name - off to skyx and be sure it
        exists, check the values are sane in the other fields then add to
        the list.
        '''
        try:
            self._updateskyx(self.tname.get())
        except SkyxObjectNotFoundError:
            tkMessageBox.showinfo(message="Can't find target: " +
                                  self.tname.get() +
                                  "\nAdd it in SkyX to continue.")
            return()
        except SkyxConnectionError:
            # We'll validate the target later before running
            pass
        if self.tname.get() and self.texposure.get() and self.tnumexp.get():
            # If it already exists delete it
            # Really should work out how to edit it in palce to not screw
            # up the order
            index = 'end'
            for item in self.ttree.get_children():
                if self.ttree.item(item)['values'][0] == self.tname.get():
                    index = self.ttree.index(item)
                    self.ttree.delete(item)
            self.ttree.insert('', index, values=[self.tname.get(),
                                                 self.texposure.get(),
                                                 self.tnumexp.get()])
        else:
            tkMessageBox.showinfo(message="Invalid Data Supplied")
        self._clear()

    def _addneoHandler(self, *args):
        for neo in self.neoobj.neocplist:
            self.ttree.insert('', 'end', values=[neo.tmpdesig, "30", "10",
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
            self.ttree.delete(item)

    def _runHandler(self):
        for target in self.ttree.get_children():
            tname = self.ttree.item(target)['values'][0]
            texp = self.ttree.item(target)['values'][1]
            tnum = self.ttree.item(target)['values'][2]
            skyx = SkyXConnection()
            if skyx.closedloopslew(tname):
                skyx.takeimages(texp, tnum)

    def _checkHandler(self):
        try:
            (fails, altfails) = self._check()
        except TypeError:
            tkMessageBox.showinfo(message="Can't get target data.")
            return (False)
        if fails:
            tkMessageBox.showinfo(message="Can't get data for: " + str(fails))
            return(False)
        elif altfails:
            tkMessageBox.showinfo(message="Targets are below horizon: " + str(altfails))
        else:
            tkMessageBox.showinfo(message="All targets OK")
            return (True)

    def _check(self):
        fails = []
        altfails = []
        for target in self.ttree.get_children():
            try:
                tname = self.ttree.item(target)['values'][0]
                [ra, dec, alt, az] = self._updateskyx(tname)
            except SkyxObjectNotFoundError:
                fails.append(self.ttree.item(target)['values'][0])
            except SkyxConnectionError, e:
                tkMessageBox.showinfo(message="Can't connect to SkyX. " +
                                      str(e) + "\nis SkyX running?")
                return(False)
            if float(alt) < 10:
                altfails.append(self.ttree.item(target)['values'][0])
        return(fails, altfails)

    def _updatePositionHandler(self, *args):
        ''' Update the positions of our Minor Planets and if necessary from
            SkyX.'''
        # TODO a lot of this class assumes that the object is in SkyX. It wont
        # always be as we dont have an API to add objects so we'll just tell
        # skyx the ra and dec
        fails = []
        for target in self.ttree.get_children():

            try:
                tname = self.ttree.item(target)['values'][0]
                texp = self.ttree.item(target)['values'][1]
                tnum = self.ttree.item(target)['values'][2]
                # Try to get data from out minor planet list. If it's not there
                # try TheSkyX
                
                mpc = MPCweb.MPCweb()
                mpc.genSmallDB(self.neoobj.neocplist)
                try:
                    # TODO: Call an update 
                    mptarget = [ l for l in self.neoobj.neocplist 
                                if tname == l.tmpdesig][0]
                    mptarget.updateephem()
                    [ra, dec, alt, az] = [mptarget.ra, mptarget.dec,
                                          mptarget.alt, mptarget.az]
                except IndexError:
                    [ra, dec, alt, az] = self._updateskyx(tname)
            except SkyxObjectNotFoundError:
                fails.append(self.ttree.item(target)['values'][0])
            except SkyxConnectionError, e:
                tkMessageBox.showinfo(message="Can't connect to SkyX. " +
                                      str(e) + "\nis SkyX running?")
                return()
            else:
                for item in self.ttree.get_children():
                    if self.ttree.item(item)['values'][0] == tname:
                        index = self.ttree.index(item)
                        self.ttree.delete(item)
                self.ttree.insert('', index, values=[tname, texp, tnum,
                                                     round(float(ra), 3),
                                                     round(float(dec), 3),
                                                     round(float(alt), 2),
                                                     round(float(az), 2)])
        if fails:
            tkMessageBox.showinfo(message="Can't find targets: " + str(fails))


    def _updateskyx(self, target):
        skyx = SkyXConnection()
        info = skyx.sky6ObjectInformation(target)
        return(info['sk6ObjInfoProp_RA_2000'], info['sk6ObjInfoProp_DEC_2000'],
               info['sk6ObjInfoProp_ALT'], info['sk6ObjInfoProp_AZM'])

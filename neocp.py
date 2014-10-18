'''
Created on 9 Sep 2014

@author: Albert
'''
from __future__ import print_function

import math

import ephem


class neo(object):
    '''
    classdocs
    '''


    def __init__(self, tmpdesig, score, discovery, ra, dec, v, updated, note,
                 observations, arc, h):
        '''
        Constructor
        '''
        self.tmpdesig = tmpdesig
        self.score = score
        self.discovery = discovery
        self.ra = ra
        self.dec = dec
        self.v = v
        self.updated = updated
        self.note = note
        self.observations = observations
        self.arc = arc
        self.h = h
        self.rate = ""
        self.pa = ""
        # self.ky6ObjectInformation skyxdata = new sky6ObjectInformation()=""
        self.alt = ""
        self.az = ""
        self.angle = ""
        self.rate = ""
        self.g = ""
        self.epoch = ""
        self.m = ""
        self.peri = ""
        self.node = ""
        self.incl = ""
        self.e = ""
        self.n = ""
        self.a = ""
        self.rarate = ""
        self.decrate = ""

    def neolist(self):
        ''' Return the target object as a list.
        '''
        return [self.tmpdesig,
                self.score,
                self.discovery,
                self.ra,
                self.dec,
                self.alt,
                self.az,
                self.angle,
                self.rate,
                self.v,
                self.updated,
                self.note,
                self.observations,
                self.arc,
                self.h]

    def addorbitdata(self, H, G, Epoch, M, Peri, Node, Incl, e, n, a):
        ''' Add given orbit data to object.
        '''
        self.h = H
        self.g = G
        self.epoch = Epoch
        self.m = M
        self.peri = Peri
        self.node = Node
        self.incl = Incl
        self.e = e
        self.n = n
        self.a = a

    def updateephem(self, timestring):
        ''' Update alt/az/ra/dec/rates/mag using pyephem
        '''
        z72 = ephem.Observer()
        z72.lon = "-6.1136"
        z72.lat = "53.2744"
        z72.elevation = 100
        z72.date = ephem.Date(timestring)
        z72.epoch = "2000"

        # Object , e, Incl., Node., Peri., a, n, e, M, decoded Epoch, D(2000),
        # H, G
        # http://scully.cfa.harvard.edu/cgi-bin/showobsorbs.cgi?Obj=VT35825&orb=y
        # Object   H     G    Epoch    M         Peri.      Node       Incl.
        #        e           n         a
        # VT35825 23.9  0.15  K14AA 354.56320  197.25360  201.41546
        # 3.99753  0.5498193  0.28428219   2.2907074
        target = ephem.readdb(self.tmpdesig + ",e," + self.incl + "," +
                              self.node + "," + self.peri + "," + self.a +
                              "," + self.n + "," + self.e + "," + self.m +"," +
                              "10/10/2014,2000,H" + self.h + "," + self.g)
        print("DEBUG Name: " + self.tmpdesig)
        target.compute(z72)
        self.alt = int(round(math.degrees(target.alt)))
        # To match the MPC format
        self.az = int(round(math.degrees(target.az))) + 180
        self.v = target.mag

        # We need to do a little more work to get the J2000 RA & Dec.
        tjnow = ephem.Equatorial(target.ra, target.dec, epoch=z72.date)
        tj2000 = ephem.Equatorial(tjnow, epoch='2000')
        self.ra = tj2000.ra
        self.dec = tj2000.dec

        # Get the location one minute later
        z72.date = z72.date+ephem.minute
        target.compute(z72)
        tjnow = ephem.Equatorial(target.ra, target.dec, epoch=z72.date)
        tj2000 = ephem.Equatorial(tjnow, epoch='2000')
        ra2 = tj2000.ra
        dec2 = tj2000.dec
        self.rarate = ra2 - self.ra
        self.decrate = dec2 - self.dec
        realrate = self.getrate(dec2)

        print("DEBUG ra1R = " + str(float(self.ra)))
        print("DEBUG ra2R = " + str(float(ra2)))
        print("DEBUG dec1R = " + str(float(self.dec)))
        print("DEBUG dec2R = " + str(float(dec2)))
        print("DEBUG rarateR = " + str(float(self.rarate)))
        print("DEBUG decrateR = " + str(float(self.decrate)))
        print("DEBUG rate = " + str(float(realrate)))

        self.rate = round(math.degrees(realrate) * 60 * 60, 2)
        self.angle = self.getpa(realrate)

    def getrate(self, dec2R):
        '''
        Based on 'Practical Astronomy with your calculator' (Duffet-Smith 1988)
        p51, but it's just a cosine rule of spherical trig. Simply
        sqrt(ra^2+dec^2) wont work, you need spherical trig not planar!
        '''
        rarateR = self.rarate
        dec1R = self.dec
        result = math.acos(math.sin(dec1R) * math.sin(dec2R) +
                           math.cos(dec1R) * math.cos(dec2R) *
                           math.cos(rarateR))
        return result

    def getpa(self, rate):
        ''' Basically :
        Sin(A)/Sin(a)=Sin(C)/sin(c)
        '''
        if self.rarate:
            aa = math.pi/2 - (self.dec + self.decrate)
            C = self.rarate
            c = rate
            try:
                ans = 180 - math.degrees(math.asin(math.sin(C) *
                                                   math.sin(aa) /
                                                   math.sin(c)))
            except ZeroDivisionError:
                print(aa)
                print(C)
                print(c)
                return 0
            if ans < 0:
                ans = 360 + ans
            return round(ans, 2)

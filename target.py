'''
Created on 9 Sep 2014

@author: Albert
'''

import datetime
import logging
import math
import time
import unittest

import ephem

import skyx
from skyx import SkyxObjectNotFoundError, SkyxConnectionError, SkyXConnection, sky6ObjectInformation

logger = logging.getLogger(__name__)


class target(object):
    '''
    classdocs
    '''

    def __init__(self, tmpdesig, ttype=None, ra=None, dec=None, 
                 nexposures=0, exposure=0):
        '''
        Constructor, Initialise everything to nothing
        '''
        self.tmpdesig = tmpdesig
        self.score = ""
        self.discovery = ""
        self.ra = ra
        self.dec = dec
        self.v = ""
        self.updated = ""
        self.note = ""
        self.observations = ""
        self.arc = ""
        self.h = ""
        self.rate = ""
        self.pa = ""
        self.alt = "0"
        self.az = "0"
        self.angle = ""
        self.rate = ""
        self.g = ""
        self.epoch = ""
        self.pyepoch = ""
        self.m = ""
        self.peri = ""
        self.node = ""
        self.incl = ""
        self.e = ""
        self.n = ""
        self.a = ""
        self.rarate = ""
        self.decrate = ""
        self.nexposures = nexposures
        self.exposure = exposure
        self.ttype = ttype

    def addneoprops(self, score, discovery, ra, dec, v, updated, note,
                    observations, arc, h):
        ''' Add the properties we get for NEO's from the MPC
        '''
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
        self.ttype = "neo"

    def addcritprops(self, epoch, e, a, incl, node, peri, m, h, g):
        ''' Add the properties that we get from pulling the critical list
        '''
        self.epoch = epoch
        [year, month, day] = self.epoch.split()
        self.pyepoch = month + "/" + day.split(".")[0] + "/" + year
        self.e = e
        self.a = a
        self.incl = incl
        self.node = node
        self.peri = peri
        self.m = m
        self.h = h
        self.g = g
        self.ttype = "mp"

    def imglist(self):
        ''' Return the target object as a list.
        '''
        return [self.tmpdesig,
                self.exposure,
                self.nexposures,
                self.ra,
                self.dec,
                self.alt,
                self.az]
                
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
        ''' Add given orbit data for neo to object.
        '''
        self.h = H
        self.g = G
        self.epoch = Epoch
        [year, month, day] = self.epoch.split()
        self.pyepoch = month + "/" + day.split(".")[0] + "/" + year
        self.m = M
        self.peri = Peri
        self.node = Node
        self.incl = Incl
        self.e = e
        self.n = n
        self.a = a

    def updateephem(self,
                    timestring=datetime.datetime.fromtimestamp(
                        round(time.time()))):
        ''' Update alt/az/ra/dec/rates/mag using pyephem
        '''
        z72 = ephem.Observer()
        z72.lon = "-6.1136"
        z72.lat = "53.2744"
        z72.elevation = 100
        z72.date = ephem.Date(timestring)
        z72.epoch = "2000"
        
        if self.ttype == "fixed":
            # We need to go to theSkyX
            try:
                conn = skyx.SkyXConnection()
                obj = skyx.sky6ObjectInformation()
                
                try:
                    conn.find(self.tmpdesig)
                    pos = obj.currentTargetRaDec(j="2000")
                    t = ephem.FixedBody()
                    t._ra = rafloat2rahours(float(pos[0]))
                    t._dec = math.radians(float(pos[1]))
                    self.ra = t._ra
                    self.dec = t._dec
                    t.compute(z72)
                    tjnow = ephem.Equatorial(target.ra, target.dec, epoch=z72.date)
                    tj2000 = ephem.Equatorial(tjnow, epoch='2000')
                    self.ra = tj2000.ra
                    self.dec = tj2000.dec
                    # Bug these are wrong
                    self.alt = t.alt
                    self.az = t.az
                except SkyxObjectNotFoundError as e:
                    logger.error(e)
                    raise
            except SkyxConnectionError as e:
                logger.error(e)
                raise
            return

        # Object , e, Incl., Node., Peri., a, n, e, M, decoded Epoch, D(2000),
        # H, G
        # http://scully.cfa.harvard.edu/cgi-bin/showobsorbs.cgi?Obj=VT35825&orb=y
        # Object   H     G    Epoch    M         Peri.      Node       Incl.
        #        e           n         a
        # VT35825 23.9  0.15  K14AA 354.56320  197.25360  201.41546
        # 3.99753  0.5498193  0.28428219   2.2907074
        target = ephem.readdb(self.tmpdesig + ",e," + self.incl + "," +
                              self.node + "," + self.peri + "," + self.a +
                              "," + self.n + "," + self.e + "," + self.m +
                              "," + self.pyepoch + ",2000,H" + self.h + "," +
                              self.g)
        logger.debug("ephem: " + self.tmpdesig + ",e," + self.incl + "," +
                     self.node + "," + self.peri + "," + self.a + "," +
                     self.n + "," + self.e + "," + self.m + "," +
                     self.pyepoch + ",2000,H" + self.h + "," + self.g)
        logger.debug("Name: " + self.tmpdesig)
        target.compute(z72)
        self.v = target.mag
        self.alt = int(round(math.degrees(target.alt)))
        self.az = int(round(math.degrees(target.az)))
        # self.v = target.mag

        # We need to do a little more work to get the J2000 RA & Dec.
        tjnow = ephem.Equatorial(target.ra, target.dec, epoch=z72.date)
        logger.debug("RA : " + str(target.ra))
        logger.debug("Dec: " + str(target.dec))
        tj2000 = ephem.Equatorial(tjnow, epoch='2000')
        self.ra = tj2000.ra
        self.dec = tj2000.dec
        logger.debug("RA : " + str(self.ra))
        logger.debug("Dec: " + str(self.dec))

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

        logger.debug("ra1R = " + str(float(self.ra)))
        logger.debug("ra2R = " + str(float(ra2)))
        logger.debug("dec1R = " + str(float(self.dec)))
        logger.debug("dec2R = " + str(float(dec2)))
        logger.debug("decrateR = " + str(float(self.decrate)))
        logger.debug("rate = " + str(float(realrate)))

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
                x = math.sin(C) * math.sin(aa) / math.sin(c)

                ans = 180 - math.degrees(math.asin(math.sin(C) *
                                                   math.sin(aa) /
                                                   math.sin(c)))
            except ZeroDivisionError:

                return 0
            except ValueError:
                # typically getting the asin of -1
                return 0
            if ans < 0:
                ans = 360 + ans
            return round(ans, 2)

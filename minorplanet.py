'''
Created on 9 Sep 2014

@author: Albert
'''
from __future__ import print_function

import math
import unittest

import ephem


class minorplanet(object):
    '''
    classdocs
    '''


    def __init__(self, tmpdesig, mptype="npc"):
        '''
        Constructor, Initialise everything to nothing
        '''
        self.tmpdesig = tmpdesig
        self.score = ""
        self.discovery = ""
        self.ra = ""
        self.dec = ""
        self.v = ""
        self.updated = ""
        self.note = ""
        self.observations = ""
        self.arc = ""
        self.h = ""
        self.rate = ""
        self.pa = ""
        self.alt = ""
        self.az = ""
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
        self.type = mptype

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
        self.type = "neo"
        
    def addcritprops(self, epoch, e, a, incl, node, peri, m, h, g):
        ''' Add the properties that we get from pulling the critical list
        '''
        self.epoch = epoch
        [year, month, day]=self.epoch.split()
        self.pyepoch = month + "/" + day.split(".")[0] + "/" + year
        self.e = e
        self.a = a
        self.incl = incl
        self.node = node
        self.peri = peri
        self.m = m
        self.h = h
        self.g = g
        self.type = "mp"
        
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
        [year, month, day]=self.epoch.split()
        self.pyepoch = month + "/" + day.split(".")[0] + "/" + year
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
                              self.pyepoch + ",2000,H" + self.h + "," + self.g)
        print("DEBUG ephem: " + self.tmpdesig + ",e," + self.incl + "," +
                              self.node + "," + self.peri + "," + self.a +
                              "," + self.n + "," + self.e + "," + self.m +"," +
                              self.pyepoch + ",2000,H" + self.h + "," + self.g)
        print("DEBUG Name: " + self.tmpdesig)
        target.compute(z72)
        self.v = target.mag
        self.alt = int(round(math.degrees(target.alt)))
        # To match the MPC format
        self.az = int(round(math.degrees(target.az))) + 180
        #self.v = target.mag

        # We need to do a little more work to get the J2000 RA & Dec.
        tjnow = ephem.Equatorial(target.ra, target.dec, epoch=z72.date)
        print("DEBUG RA : " + str(target.ra))
        print("DEBUG Dec: " + str(target.dec))
        tj2000 = ephem.Equatorial(tjnow, epoch='2000')
        self.ra = tj2000.ra
        self.dec = tj2000.dec
        print("DEBUG RA : " + str(self.ra))
        print("DEBUG Dec: " + str(self.dec))

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
            print(C)
            print(c)
            print(aa)
            try:
                x = math.sin(C) * math.sin(aa) / math.sin(c)
                print(x)
                print(math.asin(x))
                ans = 180 - math.degrees(math.asin(math.sin(C) *
                                                   math.sin(aa) /
                                                   math.sin(c)))
            except ZeroDivisionError:
                print(aa)
                print(C)
                print(c)
                return 0
            except ValueError:
                # typically getting the asin of -1
                return 0
            if ans < 0:
                ans = 360 + ans
            return round(ans, 2)
        
class Testneoephem(unittest.TestCase):
    ''' Test that our astronomical calculations are working
MPC reference data:
Date       UT   *  R.A. (J2000) Decl.  Elong.  V        Motion     Object     Sun         Moon        Uncertainty
            h                                        "/min   P.A.  Azi. Alt.  Alt.  Phase Dist. Alt.
2014 10 27 23     04 04 19.7 +19 57 46 151.3  19.5   21.76  283.7  295  +42   -48    0.18  159  -28
    '''
 
    def setUp(self):
        self.observer = ephem.Observer()
        self.observer.lon = "-6.1136"
        self.observer.lat = "53.2744"
        self.observer.elevation = 100
        self.observer.date = ephem.Date("2014-10-27 23:00:00")
        self.observer.epoch = "2000"
       
        self.target = ephem.readdb("P10frjh,e,7.43269,35.02591,162.97669," +
                                   "0.6897594,1.72051182,0.5475395," +
                                   "195.80709,10/10/2014,2000,H26.4,0.15")
        self.target.compute(self.observer)
        tjnow = ephem.Equatorial(self.target.ra, self.target.dec,
                                 epoch=self.observer.date)
        self.targetj2000 = ephem.Equatorial(tjnow, epoch='2000')
       
        self.observer.date = self.observer.date+ephem.minute
        self.target.compute(self.observer)
        tjnow = ephem.Equatorial(self.target.ra, self.target.dec,
                                 epoch=self.observer.date)
        self.targetj2000plus = ephem.Equatorial(tjnow, epoch='2000')
        self.rarate = str(float(self.targetj2000plus.ra -
                                self.targetj2000.ra))
        self.decrate = str(float(self.targetj2000plus.dec -
                                 self.targetj2000.dec))
 
       
    def test_target_ra_j2000(self):
        
        print(self.observer.date.tuple())
        print(self.target.ra)
        print(self.target.dec)
        self.assertEqual(str(self.targetj2000.ra), "4:04:21.28",
                        "Target RA is not expected value 4:04:21.28:" +
                        str(self.targetj2000.ra))
       
    def test_target_dec_j2000(self):
        self.assertEqual(str(self.targetj2000.dec), "19:57:28.5",
                        "Target RA is not expected value 19:57:28.5:" +
                        str(self.targetj2000.dec))
 
    def test_target_ra_rate(self):
        # TODO these don't match on MacOS and Win. Need to use approximate
        # comparison
        self.assertEqual(self.rarate, "-0.000109086432381",
                        "RA rate is not expected value -0.000109086432381:" +
                        self.rarate)
   
    def test_target_dec_rate(self):
        # TODO these don't match on MacOS and Win. Need to use approximate
        # comparison
        self.assertEqual(self.decrate, "2.49415833039e-05",
                        "RA rate is not expected value 2.49415833039e-05:" +
                        self.decrate)        
       
if __name__ == '__main__':
    unittest.main(verbosity=1)

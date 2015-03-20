import unittest
import arduino
import MPCweb
import platform
import os
import sys
import ephem


class TestArduinoSingleton(unittest.TestCase):
    ''' Test class to just check that the singleton is working.
    '''

    def test_singleton1(self):
        ''' Create two instances. Change self.com_port in one and verify the
            com_port is the same in both.
        '''
        testa = arduino.Arduino()
        testa.com_port = "COM1"
        testb = arduino.Arduino()
        testb.com_port = "COM2"
        self.assertEqual(testa.com_port, testb.com_port)

    def test_singleton2(self):
        ''' Create two instances. Change self.com_port in one and verify that
            it is changed when accessing the other.
        '''
        testa = arduino.Arduino()
        testa.com_port = "COM1"
        testb = arduino.Arduino()
        testb.com_port = "COM2"
        self.assertEqual(testa.com_port, "COM2")

class TestMPCWeb(unittest.TestCase):
    ''' Test the MPC web class
    '''
    
    def setUp(self):
        # TODO fix these paths
        if os.name == 'nt':
            ncp="file://" + "/Users\Albert\workspace\AutoSkyX" + "\\test_data\\neocp.txt"
            cl="file://" + "/Users\Albert\workspace\AutoSkyX" + "\\test_data\\Soft06CritList.txt"
        else:
            ncp=os.getcwd() + "/neocp.txt"
            cl=os.getcwd() + "/Soft06CritList.txt"
        my_mpc = MPCweb.MPCweb(neocp=ncp,
                               crits=cl)
        self.neos = my_mpc.get_neocp()
        self.crits = my_mpc.get_crits()

        for neo in self.neos:
            if neo.tmpdesig == "P10jAnu":
                self.target = neo

        for crit in self.crits:
            if crit.tmpdesig == "1915 1953 EA":
                self.crit = crit

    def test_get_neocp_score(self):
        ''' test getting the neocplist score'''
        self.assertEqual(self.target.score, "100")

    def test_get_neocp_discovery(self):
        ''' test getting the neocplist discovery'''
        self.assertEqual(self.target.discovery, "2015 03 14.3")

    def test_get_neocp_ra(self):
        ''' test getting the neocplist ra'''
        self.assertEqual(self.target.ra, " 10.5195")

    def test_get_neocp_dec(self):
        ''' test getting the neocplist dec'''
        self.assertEqual(self.target.dec, "+14.5880")

    def test_get_neocp_h(self):
        ''' test getting the neocplist h'''
        self.assertEqual(self.target.h, "22.3")

    def test_crit_desig(self):
        ''' test getting critical h'''
        self.assertEqual(self.crit.h, "18.97")

    def test_crit_peri(self):
        ''' test getting critical peri'''
        self.assertEqual(self.crit.peri, "347.8218 ")

    def test_crit_node(self):
        ''' test getting critical node'''
        self.assertEqual(self.crit.node, "162.9641 ")

    def test_crit_epoch(self):
        ''' test getting critical epoch'''
        self.assertEqual(self.crit.epoch, "2014 05 23.000")

    def test_crit_m(self):
        ''' test getting critical m'''
        self.assertEqual(self.crit.m, " 81.2615  ")

    def test_crit_a(self):
        ''' test getting critical a'''
        self.assertEqual(self.crit.a, "2.544736")


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

        self.assertEqual(str(self.targetj2000.ra), "4:04:21.28",
                         "Target RA is not expected value 4:04:21.28:" +
                         str(self.targetj2000.ra))

    def test_target_dec_j2000(self):
        self.assertEqual(str(self.targetj2000.dec), "19:57:28.5",
                         "Target RA is not expected value 19:57:28.5:" +
                         str(self.targetj2000.dec))

    def test_target_ra_rate(self):
        self.assertEqual(self.rarate[:14], "-0.00010908643",
                         "RA rate is not expected value -0.00010908643:" +
                         self.rarate[:14])

    def test_target_dec_rate(self):
        self.assertEqual(self.decrate[:9], "2.4941583",
                         "RA rate is not expected value 2.4941583:" +
                         self.decrate[:9])

    # TODO: Test to take an neocp target and gets its position,
    #        verify against skyx
    # TODO: Test to take an critlist target and gets its position,
    #        verify against skyx
if __name__ == '__main__':
    
    if platform.architecture()[0] == '64bit':
        print("We can't run on 64bit sorry")
        sys.exit(1)
    unittest.main()

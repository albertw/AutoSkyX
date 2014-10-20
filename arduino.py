''' Module to handle the Arduino. Implemented as a singleton so we can
    instantiate the class anywhere and have the right data.
    Basic idea found in
    http://www.mindviewinc.com/Books/Python3Patterns/Index.php
'''

import unittest

class Singleton(object):
    ''' Singleton class '''
    def __init__(self, klass):
        ''' Initiator '''
        self.klass = klass
        self.instance = None
    def __call__(self, *args, **kwds):
        ''' When called as a function return our singleton instance. '''
        if self.instance == None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


@Singleton
class Arduino(object):
    ''' Class to handle communication with the Arduino. '''
    def __init__(self):
        self.com_port = ""


class TestArduino(unittest.TestCase):
    ''' Test class to check the singleton.
    '''

    def test_singleton1(self):
        ''' Create two instances. Change self.com_port in one and verify that
            it is changed when accessing the other.
        '''
        testa = Arduino()
        testa.com_port = "COM1"
        testb = Arduino()
        testb.com_port = "COM2"

        self.assertEqual(testa.com_port, testb.com_port)


if __name__ == '__main__':
    unittest.main()

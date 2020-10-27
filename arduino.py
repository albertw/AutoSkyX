''' Module to handle the Arduino. Implemented as a singleton so we can
    instantiate the class anywhere and have the right data.
    Basic idea found in
    http://www.mindviewinc.com/Books/Python3Patterns/Index.php
'''
import logging
import unittest
import serial

log = logging.getLogger(__name__)


class ArduinoUnparseableOutput(Exception):
    ''' Exception for when received lines from the arduino do not
        start with "ARDUINO:".
        Turning debug output on on the arduino will cause this to happen
        so it's envisaged that for debugging work you will be working directly
        on the serial console not though this module.
    '''
    def __init__(self, value):
        ''' init'''
        super(ArduinoUnparseableOutput, self).__init__(value)
        self.value = value

    def __str__(self):
        ''' returns the error string '''
        return repr(self.value)


class Singleton(object):
    ''' Singleton class '''
    def __init__(self, klass):
        ''' Initiator '''
        # When we load the module and decorated classes call this __init__()
        # setting self.klass to the decorated class
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        ''' When called as a function return our singleton instance. '''
        # When a new object is created of the decorated class __call__()
        # is called. We check if we already have an instance and if we do
        # we return it.
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
            # The above line is actually what calls Arduino.__init__
            # So only gets called the first time we create and Arduino
            # instance.
        return self.instance


@Singleton
class Arduino(object):
    ''' Class to handle communication with the Arduino. '''
    def __init__(self):
        self.com_port = ""
        self.ser = None

    def connect(self, serialport="COM8"):
        ''' Connect to the serial port arduino and read off the first two
            lines.
        '''
        self.com_port = serialport
        log.debug("Com port" + str(self.com_port))
        self.ser = serial.Serial(self.com_port, 9600)
        log.debug(self.ser.readline())
        log.debug(self.ser.readline())

    def isconnected(self):
        if self.ser:
            return True
        else:
            return False

    def disconnect(self):
        ''' Disconnect serial connection to arduino.
        '''
        # TODO disabled for now by defaults
        # self.ser.close()
        pass

    def __get_serial_line(self):
        ''' Read a line from the serial port. Raise exception if it does
            not start with the string "ARDUINO:".
        '''
        output = self.ser.readline()
        if output.startswith("ARDUINO:"):
            return output.strip()
        else:
            raise ArduinoUnparseableOutput(str(output))

    def __write(self, string):
        ''' Save us having to add a \n to everything
        '''
        return self.ser.write(string + '\n')

    def get_temperatures(self):
        ''' Get the temperature string from the arduino.
        '''
        self.__write('c')
        output = self.__get_serial_line().split(":")
        try:
            return(output[2], output[4])
        except IndexError as msg:
            raise IndexError(str(msg) + str(output))

    def set_speed(self, speed):
        ''' Set the speed of the motor.
            Valid values are 0-255.
        '''
        if speed < 0 or speed > 255:
            raise RuntimeError("Invalid speed given.")
        self.__write("s" + str(int(speed)))
        output = self.__get_serial_line().split(":")
        return output[2]

    def set_pulse_duration(self, pulse):
        ''' Set the pulse duration (ms) of the motors.
            Block any requests over 5s. A special value of -1 is accepted
            for continuous operation, but the arduino will limit this to 5s.
        '''
        if pulse > 5000:
            raise RuntimeError("Too long a pulse " + str(int(pulse)))
        self.__write("d" + str(int(pulse)))
        output = self.__get_serial_line().split(":")
        return output[2]

    def send_char(self, char):
        ''' Send a single character to the arduino.
            We check for valid inputs.
        '''
        if char not in 'qwertyuSD':
            raise RuntimeError("Invalid character" + char)
        self.__write(char)
        output = self.__get_serial_line()
        return output


class TestArduino(unittest.TestCase):
    ''' Test class to check the arduino.
        Requires that Arduino be connected to the correct Serial/COM port!
    '''
    @classmethod
    def setUpClass(cls):
        ''' Set up the connection for tests.
        '''
        cls.testa = Arduino()
        cls.testa.connect()

    @classmethod
    def tearDownClass(cls):
        ''' Disconnect after testing.
        '''
        cls.testa.disconnect()

    def test_tmps(self):
        ''' Test reading the temperatures from the sensors.
        '''
        try:
            self.testa.get_temperatures()
        except ArduinoUnparseableOutput as msg:
            self.assertEqual(True, False, "Unparseable Output " + str(msg))
        except IndexError as msg:
            self.assertEqual(True, False, "Output not as expected:" + str(msg))

    def test_set_speed(self):
        ''' Test setting the speed of the motor.
        '''
        try:
            ret = self.testa.set_speed(100)
            self.assertEqual(ret, "98", "Set speed does not match.")
        except ArduinoUnparseableOutput as msg:
            self.assertEqual(True, False, "Unparseable Output " + str(msg))
        except IndexError as msg:
            self.assertEqual(True, False, "Output not as expected:" + str(msg))

    def test_set_speed2(self):
        ''' Test setting the speed of the motor.
        '''
        try:
            self.testa.set_speed(500)
        except RuntimeError as msg:
            self.assertEqual("Invalid speed given.", str(msg), str(msg))
        else:
            self.assertEqual(True, False, "Output not as expected:" + str(msg))

    def test_set_pulse_duration(self):
        ''' Test setting the duration of the motor.
        '''
        try:
            ret = self.testa.set_pulse_duration(100)
            self.assertEqual(ret, "100", "Set duration does not match.")
        except ArduinoUnparseableOutput:
            self.assertEqual(True, False, "ArduinoUnparseableOutput caught.")
        except IndexError as msg:
            self.assertEqual(True, False, "Output not as expected:" + str(msg))

    def test_set_pulse_duration2(self):
        ''' Test setting the duration of the motor.
        '''
        try:
            self.testa.set_pulse_duration(60000)
        except RuntimeError as msg:
            self.assertTrue(str(msg).startswith("Too long a pulse"), str(msg))
        else:
            self.assertEqual(True, False, "Output not as expected:" + str(msg))

    def test_motor_commands(self):
        ''' Test moving the motor forwards.
        '''
        try:
            self.testa.set_speed(100)
            self.testa.set_pulse_duration(100)
            ret = self.testa.send_char('e')
            # TODO Redo with final motor message
            self.assertTrue(ret.startswith("ARDUINO:Moved motor:"),
                            "Moved Motor message not received.")
        except ArduinoUnparseableOutput:
            self.assertEqual(True, False, "ArduinoUnparseableOutput caught.")
        except IndexError as msg:
            self.assertEqual(True, False, "Output not as expected:" + str(msg))

    def test_motor_commands2(self):
        ''' Test moving the motor backwards.
        '''
        try:
            self.testa.set_speed(100)
            self.testa.set_pulse_duration(100)
            ret = self.testa.send_char('t')
            # TODO Redo with final motor message
            self.assertTrue(ret.startswith("ARDUINO:Moved motor:"),
                            "Moved Motor message not received.")
        except ArduinoUnparseableOutput:
            self.assertEqual(True, False, "ArduinoUnparseableOutput caught.")
        except IndexError as msg:
            self.assertEqual(True, False, "Output not as expected:" + str(msg))

    def test_motor_commands3(self):
        ''' Test moving the motor backwards.
        '''
        try:
            ret = self.testa.send_char('r')
            # TODO Redo with final motor message
            self.assertTrue(ret.startswith("ARDUINO:Stopped motor:"),
                            "Stopped Motor message not received.")
        except ArduinoUnparseableOutput:
            self.assertEqual(True, False, "ArduinoUnparseableOutput caught.")
        except IndexError as msg:
            self.assertEqual(True, False, "Output not as expected:" + str(msg))

    def test_sendchar(self):
        ''' send an invalid character.
        '''
        try:
            self.testa.send_char('b')
        except RuntimeError as msg:
            self.assertTrue(str(msg).startswith("Invalid character"), str(msg))
        else:
            self.assertEqual(True, False, "Output not as expected:")


if __name__ == '__main__':
    unittest.main(verbosity=1)

''' Method to handle connections to TheSkyX
'''


import logging
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, error


logger = logging.getLogger(__name__)


class SkyxObjectNotFoundError(Exception):
    ''' Exception for objects not found in SkyX.
    '''
    def __init__(self, value):
        ''' init'''
        super(SkyxObjectNotFoundError, self).__init__(value)
        self.value = value

    def __str__(self):
        ''' returns the error string '''
        return repr(self.value)


class SkyxConnectionError(Exception):
    ''' Exception for Failures to Connect to SkyX
    '''
    def __init__(self, value):
        ''' init'''
        super(SkyxConnectionError, self).__init__(value)
        self.value = value

    def __str__(self):
        ''' returns the error string '''
        return repr(self.value)


class SkyXConnection(object):
    ''' Class to handle connections to TheSkyX
    '''
    def __init__(self, host="192.168.1.123", port=3040):
        ''' define host and port for TheSkyX.
        '''
        self.host = host
        self.port = port

    def send(self, command):
        ''' sends a js script to TheSkyX and returns the output.
        '''
        try:
            logger.debug(command)
            sockobj = socket(AF_INET, SOCK_STREAM)
            sockobj.connect((self.host, self.port))
            sockobj.send(bytes('/* Java Script */\n' +
                               '/* Socket Start Packet */\n' + command +
                               '\n/* Socket End Packet */\n'))
            oput = sockobj.recv(2048)
            logger.debug(oput)
            sockobj.shutdown(SHUT_RDWR)
            sockobj.close()
            return oput
        except error as msg:
            raise SkyxConnectionError(msg)

    def closedloopslew(self, target):
        ''' Perform a lcosed loop slew.
            Slew, take image, solve, slew, take image, confirm.
        '''
        # 0 on success
        command = '''
            sky6StarChart.Find("''' + target + '''");
            ClosedLoopSlew.exec();
            '''
        oput = self.send(command)
        for line in oput.splitlines():
            if line == "0":
                return True
            if "5005" in line:
                raise SkyxObjectNotFoundError("Object not found.")
            if "Receive time-out" in line:
                raise SkyxObjectNotFoundError("Time out getting image.")
        # God knows if we are here...
        return True

    def takeimages(self, exposure, nimages):
        ''' Take a given number of images of a specified exposure.
        '''
        command = """
        var Imager = ccdsoftCamera;
        function TakeOnePhoto()
        {
            Imager.Connect();
            Imager.ExposureTime = """+str(exposure)+"""
            Imager.Asynchronous = 0;
            Imager.TakeImage();
        }

        function Main()
        {
            for (i=0; i<"""+str(nimages)+"""; ++i)
            {
                TakeOnePhoto();
            }
        }

        Main();
        """
        # TODO
        oput = self.send(command)
        for line in oput.splitlines():
            pass
        pass

    def sky6ObjectInformation(self, target):
        ''' Method to return basic SkyX position information on a target.
        '''
        command = """
                var Target = \"""" + target + """\";
                var Target56 = 0;
                var Target57 = 0;
                var Target58 = 0;
                var Target59 = 0;
                var Target77 = 0;
                var Target78 = 0;
                var Out = "";
                var err;
                sky6StarChart.LASTCOMERROR = 0;
                sky6StarChart.Find(Target);
                err = sky6StarChart.LASTCOMERROR;
                if (err != 0) {
                            Out = Target + " not found."
                } else {
                            sky6ObjectInformation.Property(56);
                            Target56 = sky6ObjectInformation.ObjInfoPropOut;
                            sky6ObjectInformation.Property(57);
                            Target57 = sky6ObjectInformation.ObjInfoPropOut;
                            sky6ObjectInformation.Property(58);
                            Target58 = sky6ObjectInformation.ObjInfoPropOut;
                            sky6ObjectInformation.Property(59);
                            Target59 = sky6ObjectInformation.ObjInfoPropOut;
                            sky6ObjectInformation.Property(77);
                            Target77 = sky6ObjectInformation.ObjInfoPropOut;
                            sky6ObjectInformation.Property(78);
                            Target78 = sky6ObjectInformation.ObjInfoPropOut;
                            Out = "sk6ObjInfoProp_RA_2000:"+String(Target56)+
                            "\\nsk6ObjInfoProp_DEC_2000:"+String(Target57)+
                            "\\nsk6ObjInfoProp_AZM:"+String(Target58)+
                            "\\nsk6ObjInfoProp_ALT:"+String(Target59)+
                            "\\nsk6ObjInfoProp_RA_RATE_ASPERSEC:"+String(Target77)+
                            "\\nsk6ObjInfoProp_DEC_RATE_ASPERSEC:"+String(Target78)+"\\n";

                }
                """
        results = {}
        oput = self.send(command)
        for line in oput.splitlines():
            if "Object not found" in line:
                raise SkyxObjectNotFoundError("Object not found.")
            if ":" in line:
                info = line.split(":")[0]
                val = line.split(":")[1]
                results[info] = val
        return results

    def test1(self):
        ''' basic test
        '''
        command = """
/* Java Script */
var Out;
var PropCnt = 189;
var p;

Out="";
sky6StarChart.Find("Saturn");

for (p=0;p<PropCnt;++p)
{
   if (sky6ObjectInformation.PropertyApplies(p) != 0)
    {
        /*Latch the property into ObjInfoPropOut*/
      sky6ObjectInformation.Property(p)

        /*Append into s*/
      Out += sky6ObjectInformation.ObjInfoPropOut + "|"

        //print(p);
   }
}"""
        print (self.send(command))


if __name__ == "__main__":
    xconn = SkyXConnection()
    print(xconn.sky6ObjectInformation("Saturn"))

from socket import *

class SkyXConnection():
      
    def __init__(self, host="localhost", port=3040):
        self.host = host
        self.port = port
        
    def send(self, command):
        sockobj = socket(AF_INET, SOCK_STREAM)
        sockobj.connect((self.host, self.port))
        sockobj.send(bytes("/* Java Script */\n" + command))
        op = sockobj.recv(2048)    
        sockobj.shutdown(SHUT_RDWR)  
        sockobj.close()
        return op
        
    def sky6ObjectInformation(self, target):
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
                            "\\nsk6ObjInfoProp_DEC_RATE_ASPERSEC:"+String(Target78);

                }
                """

        print (self.send(command))
        
                
    def test1(self):
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
    x = SkyXConnection()
    x.sky6ObjectInformation("Saturn")

    
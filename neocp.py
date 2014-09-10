'''
Created on 9 Sep 2014

@author: Albert
'''
import SkyXConnection
import math
import datetime

class neo(object):
    '''
    classdocs
    '''


    def __init__(self, tmpdesig,score,discovery,ra,dec,v,updated,note,observations,arc,h):
        '''
        Constructor
        '''
        self.tmpdesig=tmpdesig
        self.score=score
        self.discovery=discovery
        self.ra=ra
        self.dec=dec
        self.v=v
        self.updated=updated
        self.note=note
        self.observations=observations
        self.arc=arc
        self.h=h
        self.rate=""
        self.pa=""
        #self.ky6ObjectInformation skyxdata = new sky6ObjectInformation()=""
        self.alt=""
        self.az=""
        self.angle=""
        self.rate=""
        self.g=""
        self.epoch=""
        self.m=""
        self.peri=""
        self.node=""
        self.incl=""
        self.e=""
        self.n=""
        self.a=""
        self.rarate=""
        self.decrate=""
        
    def neolist(self):
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
        self.h=H
        self.g=G
        self.epoch=Epoch
        self.m=M
        self.peri=Peri
        self.node=Node
        self.incl=Incl
        self.e=e
        self.n=n
        self.a=a
        
        
    def updateskyxinfo(self):
        skyx = SkyXConnection.SkyXConnection()
        skyxinfo=skyx.sky6ObjectInformation(self.tmpdesig)
        self.az=round(float(skyxinfo['sk6ObjInfoProp_AZM']),2)
        self.alt=round(float(skyxinfo['sk6ObjInfoProp_ALT']),2)
        self.ra=round(float(skyxinfo['sk6ObjInfoProp_RA_2000']),3)
        self.dec=round(float(skyxinfo['sk6ObjInfoProp_DEC_2000']),3)
        self.rarate=skyxinfo['sk6ObjInfoProp_RA_RATE_ASPERSEC']
        self.decrate=skyxinfo['sk6ObjInfoProp_DEC_RATE_ASPERSEC']
        self.rate=self.getRate()
        self.angle=self.getPa()
        self.updated=datetime.datetime.now().strftime("From SkyX %b %d %H:%M %Z")
        
    def getRate(self):
        '''
        Based on 'Practical Astronomy with your calculator' (Duffet-Smith 1988) 
        p51, but it's just a cosine rule of spherical trig. Simply 
        sqrt(ra^2+dec^2) wont work, you need spherical trig not planar!
        '''
        if self.rarate:
            rarateR=math.radians(float(self.rarate))
            dec1R = math.radians(float(self.dec))
            dec2R = math.radians(float(self.decrate) + float(self.dec ))
            result = math.degrees(
                     math.acos(
                        math.sin(dec1R) * math.sin(dec2R) + math.cos(dec1R) * math.cos(dec2R) * math.cos(rarateR)     
                               )                
                                  )
            return round((((result * 60) * 100.0) / 100.0),2)
        
    def getPa(self):
        ''' Basically :
        Sin(A)/Sin(a)=Sin(C)/sin(c)
        '''
        if self.rarate:            
            
            aa = math.radians(90 - (float(self.dec) + float(self.decrate)))
            C = math.radians(float(self.rarate))
            c = math.radians(float(self.rate)/60)
            ans = math.degrees(math.asin(
                       math.sin(C) * math.sin(aa) / math.sin(c)                  
                       ))
            if ans < 0:
                ans = 360 + ans
            return round(ans,2)
            
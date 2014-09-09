'''
Created on 9 Sep 2014

@author: Albert
'''
from compiler.ast import Node

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
        
        
        

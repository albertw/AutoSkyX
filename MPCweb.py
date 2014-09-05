import urllib2
import neocp
import re
import pprint

class MPCweb():
    
    def __init__(self, pcp="http://www.minorplanetcenter.net/iau/NEO/pccp.txt", neocp="http://www.minorplanetcenter.net/iau/NEO/neocp.txt"):
        self.pcp = pcp
        self.neocp = neocp
        
    def getpcp(self):
        data = urllib2.urlopen(self.pcp)
        for line in data:
            print line
    
    def getneocp(self):
        data = urllib2.urlopen(self.neocp)
        regex = re.compile("^(.{7}) (.{3}) "
                    + "(.{12}) (.{8}) (.{8}) (.{4}) (.{21})  (.{7}) "
                    + "(.{3})  (.{5}) (.{4})")
        neos = []
        for line in data:
            res = regex.match(line)
            tmpneo = neocp.neo()
            tmpneo.tmpdesig = res.group(1)
            tmpneo.score = res.group(2)
            tmpneo.discovery = res.group(3)
            tmpneo.ra = res.group(4)
            tmpneo.dec = res.group(5)
            tmpneo.v = res.group(6)
            tmpneo.updated = res.group(7)
            tmpneo.note = res.group(8)
            tmpneo.observations = res.group(9)
            tmpneo.arc = res.group(10)
            tmpneo.h = res.group(11)
            neos.append(tmpneo)
        return neos


if __name__ == "__main__":
    x = MPCweb()
    neos = x.getneocp()
    for neo in neos:
        pprint.pprint(vars(neo))
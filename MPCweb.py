import urllib2
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
            neo = (res.group(1), res.group(2), res.group(3), res.group(4),
                  res.group(5), "", "", "", "", res.group(6), res.group(7), 
                  res.group(8), res.group(9), res.group(10), res.group(11))
            neos.append(neo)
        return neos


if __name__ == "__main__":
    x = MPCweb()
    neos = x.getneocp()
    for neo in neos:
        pprint.pprint(vars(neo))

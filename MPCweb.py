""" Mpdule to interface with the MPC website
"""

import logging
import pprint
import re
import urllib.error
import urllib.parse
import urllib.request

import target

logger = logging.getLogger(__name__)


class MPCweb(object):
    """ Class to interface with the MPC website
    """

    def __init__(self, pcp="http://www.minorplanetcenter.net/iau/NEO/pccp.txt",
                 neocp="http://www.minorplanetcenter.net/iau/NEO/neocp.txt",
                 crits="http://www.minorplanetcenter.net/iau/Ephemerides/CritList/Soft06CritList.txt"):
        self.pcp = pcp
        self.neocp = neocp
        self.crits = crits

    def get_pcp(self):
        """ Get the Potential Comet data.
        """
        data = urllib.request.urlopen(self.pcp)
        for line in data:
            logger.debug(line)

    def get_neocp(self):
        """ Get the NEOCP data
        """
        data = urllib.request.urlopen(self.neocp).readlines()
        regex = re.compile("^(.{7}) (.{3}) (.{12}) (.{8}) (.{8}) (.{4})" +
                           " (.{22}) (.{7}) (.{3}) (.{6}) (.{4})")
        my_neos = []
        for line in data:
            res = regex.match(line.decode('UTF-8'))
            my_neo = target.target(res.group(1).strip())
            my_neo.addneoprops(res.group(2), res.group(3),
                               res.group(4), res.group(5), res.group(6),
                               res.group(7), res.group(8), res.group(9),
                               res.group(10), res.group(11))
            my_neos.append(my_neo)
        return my_neos

    def get_crits(self):
        """ Get the Critical List data.
        """
        data = urllib.request.urlopen(self.crits)
        regex = re.compile(
            "^(.{21})\|(.{14})\|(.{10})\|(.{8})\|(.{8})\|(.{9})\|(.{9})\|(.{5})\|(.{10})\|(.{5})\|(.{5})")
        crits = []
        for line in data:
            res = regex.match(line)
            logger.debug(line)
            logger.debug(res.group(2))
            crit = target.target(res.group(1).strip(), ttype="mp")
            logger.debug(res.group(2) + " " + res.group(3) + " " +
                         res.group(4) + " " + res.group(5) + " " +
                         res.group(6) + " " + res.group(7) + " " +
                         res.group(9) + " " + res.group(10) + " " +
                         res.group(11))
            crit.addcritprops(res.group(2), res.group(3), res.group(4),
                              res.group(5), res.group(6), res.group(7),
                              res.group(9), res.group(10), res.group(11))
            crits.append(crit)
        return crits

    def gen_findorb(self, neocplist):
        """ Generate the FindOrb format database.
        """
        findorbdb = ""
        for item in neocplist:
            url = "http://scully.cfa.harvard.edu/cgi-bin/showobsorbs.cgi?Obj=" \
                  + item.tmpdesig + "&obs=y"
            data = urllib.request.urlopen(url)
            for line in data:
                if "html" not in line:
                    findorbdb = findorbdb + line
        return findorbdb

    def unpack_epoch(self, packed):
        """ Unpack the MPC epoch format.
        """
        ehash = {'1': '01',
                 '2': '02',
                 '3': '03',
                 '4': '04',
                 '5': '05',
                 '6': '06',
                 '7': '07',
                 '8': '08',
                 '9': '09',
                 'A': '10',
                 'B': '11',
                 'C': '12',
                 'D': '13',
                 'E': '14',
                 'F': '15',
                 'G': '16',
                 'H': '17',
                 'I': '18',
                 'J': '19',
                 'K': '20',
                 'L': '21',
                 'M': '22',
                 'N': '23',
                 'O': '24',
                 'P': '25',
                 'Q': '26',
                 'R': '27',
                 'S': '28',
                 'T': '29',
                 'U': '30',
                 'V': '31'}

        regex = re.compile("(.)(..)(.)(.)")
        matches = regex.match(packed)

        year = ehash[matches.group(1)] + matches.group(2)
        month = ehash[matches.group(3)]
        day = ehash[matches.group(4)]
        datestr = year + " " + month + " " + day + ".000"
        return datestr

    def gen_smalldb(self, neocplist):
        """ Download orbit data, store it in objects, and return a smalldb.
        """
        smalldb = ""
        for item in neocplist:
            if item.ttype == "neo":
                # g should be populated if we got the orbit data before
                if item.g == "":
                    url = "https://cgi.minorplanetcenter.net/cgi-bin/showobsorbs.cgi?Obj=" \
                          + item.tmpdesig + "&orb=y"
                    logger.debug(url)
                    data = urllib.request.urlopen(url).readlines()
                    for line in data:
                        line = line.decode("UTF-8")
                        if "NEOCPNomin" in line:
                            values = line.split()
                            item.addorbitdata(values[1], values[2],
                                              self.unpack_epoch(values[3]),
                                              values[4], values[5], values[6],
                                              values[7], values[8], values[9],
                                              values[10])
                            dbline = "  %-19.19s|%-14.14s|%8.6f  |%8f|%8.4f|%8.4f |%8.4f| 2000|%9.4f  |%5.2f|%-5.2f|   0.00\n" % (
                                values[0], self.unpack_epoch(values[3]),
                                float(values[8]), float(values[10]),
                                float(values[7]), float(values[6]),
                                float(values[5]), float(values[4]),
                                float(values[1]), float(values[2]))
                            logger.debug(dbline)
                            smalldb = smalldb + dbline
                            break
                else:
                    # We already have it. Return the db ine
                    dbline = "  %-19.19s|%-14.14s|%8.6s  |%8s|%8.4s|%8.4s |%8.4s| 2000|%9.4s  |%5.2s|%-5.2s|   0.00\n" % (
                        item.tmpdesig, item.epoch, item.e, item.a, item.incl,
                        item.node, item.peri, item.m, item.h, item.g)
                    logger.debug(dbline)
                    smalldb = smalldb + dbline
            elif item.ttype == "mp":  # regular minor planet
                dbline = "  %-19.19s|%-14.14s|%8.6f  |%8f|%8.4f|%8.4f |%8.4f| 2000|%9.4f  |%5.2f|%-5.2f|   0.00\n" % (
                    item.tmpdesig, item.epoch, float(item.e), float(item.a),
                    float(item.incl), float(item.node), float(item.peri),
                    float(item.m), float(item.h), float(item.g))
                logger.debug(item.peri)
                logger.debug(type(item.peri))
                logger.debug(dbline)
                smalldb = smalldb + dbline
            else:
                # TODO possibly go to skyx if we can
                pass

        return smalldb


if __name__ == "__main__":
    MPC = MPCweb()
    NEOS = MPC.get_neocp()
    for neo in NEOS:
        pprint.pprint(vars(neo))

import urllib2
import pprint
import re


def unpackEpoch(packed):
    year="0000"
    month="00"
    day="00"
    hash={'1':'01',
          '2':'02',
          '3':'03',
          '4':'04',
          '5':'05',
          '6':'06',
          '7':'07',
          '8':'08',
          '9':'09',
          'A':'10',
          'B':'11',
          'C':'12',
          'D':'13',
          'E':'14',
          'F':'15',
          'G':'16',
          'H':'17',
          'I':'18',
          'J':'19',
          'K':'20',
          'L':'21',
          'M':'22',
          'N':'23',
          'O':'24',
          'P':'25',
          'Q':'26',
          'R':'27',
          'S':'28',
          'T':'29',
          'U':'30',
          'V':'31'}
    
    regex = re.compile("(.)(..)(.)(.)")
    matches = regex.match(packed)
    
    year = hash[matches.group(1)]+matches.group(2)
    month = hash[matches.group(3)]
    day = hash[matches.group(4)] 
    datestr= year +" " + month + " " + day + ".000"
    print datestr
    return datestr
    
def genSmallDB(neocplist):
    smalldb=""
    for item in neocplist:
        url = "http://scully.cfa.harvard.edu/cgi-bin/showobsorbs.cgi?Obj=" \
                        + item.tmpdesig + "&orb=y"
        data = urllib2.urlopen(url)
        for line in data:
            if "NEOCPNomin" in line:
                values=line.split()
                item.addorbitdata(values[1],values[2],values[3],values[4],values[5],values[6],values[7],values[8],values[9],values[10])
                dbline = "  %-19.19s|%-14.14s|%8.6f  |%8f|%8.4f|%8.4f |%8.4f| 2000|%9.4f  |%5.2f|%-5.2f|   0.00\n" % (
                          values[0],unpackEpoch(values[3]),float(values[8]),float(values[10]),
                          float(values[7]),float(values[6]),float(values[5]),float(values[4]),float(values[1]),float(values[2]))
                smalldb = smalldb + dbline
    return smalldb
    
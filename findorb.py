import urllib2

def genfindorb(neocplist):
    findorbdb = ""
    for item in neocplist:
        url = "http://scully.cfa.harvard.edu/cgi-bin/showobsorbs.cgi?Obj=" \
                        + item.tmpdesig + "&obs=y"
        data = urllib2.urlopen(url)
        for line in data:
            if "html" not in line:
                findorbdb = findorbdb + line
    return findorbdb
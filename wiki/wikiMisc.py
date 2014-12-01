import re, time, urllib, json
import wikiSettings

def escapeName(name):
    result = name.replace(' ', '_')
    return result

def unEscapeName(name):
    result = name.replace('_', ' ')
    return result

def unescapeHTML(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s
def escapeHTML(s):
    s = s.replace(" ", "%20")
    return s

# check if the given string is suitable for an wiki article name
def isArticleName(s):
    notAlloweds = ':;,|\n\t'

    for c in notAlloweds:
        if c in s:
            return False
    return True

# only accept the traditional WikiName only.
def isWikiName(s):
    r1 = re.compile('([A-Z][a-z]+){2,}[ \n\t$]')
    return r1.match(s)

def findURI(s):
    uri_regex = re.compile('https?://[^ \n\t$]{2,}')
    search = uri_regex.search(s)
    if search != None:
        return search.start()
    else:
        return -1


# this function only checks if the given string is a valid HTTP URI
def isURI(s):
    # do not allow any URI with whitespace character
    if s.find(' ') >= 0:
        return False
    else:
        uri_regex = re.compile('^https?://.{2,}')
        if uri_regex.match(s):
            return True
        else:
            return False

def bar2Dict(bar_str):
    s = bar_str.split('|')
    s = [e.split('\n') for e in s]
    s = [x.strip() for l in s for x in l]
    print bar_str
    print s
  
    result = {}
    l = []
    for item in s:
        v = item.split(': ')
        if len(v) == 2:
            result[v[0]] = v[1].strip()
        else:
            l.append(v[0].strip())
    return (result, l)

def spellCorrection(string):
    url = \
    'http://search.yahooapis.com/WebSearchService/V1/spellingSuggestion?appid=%s&query=%s&output=json&callback=?' % (wikiSettings.yahoo_api_id, urllib.quote(string.encode('utf8')))
    f = urllib.urlopen(url)
    jsonStr = f.read()[1:-2] # to remove ( and ); in the string
    f.close()
    corrections = json.loads(jsonStr)
    if corrections['ResultSet'] == '':
        return None
    else:
        return corrections['ResultSet']['Result']

def addLog(filename, addr, action, article):
    fp = open(filename, 'a')
    fp.write('%s\t%s\t%s\t%s\n'% (time.strftime("%Y.%m.%e %H:%M:%S"), addr, action, article.encode('utf8')))
    fp.close()

# check if the given IP addr is blocked or not.
def isBlockedIP(ipAddr, blockPatterns=wikiSettings.blocked_IPs):
    for p in blockPatterns:
        pattern = p.replace('.', '\.')
        pattern = pattern.replace('*', '[0-9]{1,3}')
        r = re.compile(pattern)
        if r.match(ipAddr) != None:
            return True
    return False


def checkReferrer(referrerURI):
    return 0

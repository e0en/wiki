import sgmllib

def get_favicon_url(url):
    """
    Get the favicon used for site at url.
    - First try parsing for a favicon link in the html head.
    - Then try just /favicon.ico.
    - If neither found, return None
    """
    class FaviconFinder(sgmllib.SGMLParser):
        """
        A Parser class for finding the favicon used (if specified).
        """
        
        def __init__(self, verbose=0):
            sgmllib.SGMLParser.__init__(self, verbose)
            self.favicon_url = None

        def start_link(self, attributes):
            attributes = dict(attributes)
            if not self.favicon_url:
                if 'rel' in attributes and 'icon' in attributes['rel']:
                    if 'href' in attributes:
                        self.favicon_url = attributes['href']
                elif 'rel' in attributes and 'shortcut icon' in attributes['rel']:
                    if 'href' in attributes:
                        self.favicon_url = attributes['href']
    # Try to parse html at url and get favicon
    if not url.startswith('http://') or url.startswith('https://'):
        url = 'http://%s' % url
    try:
        site = urllib.urlopen(url)
        contents = site.read()
    
        favicon_parser = FaviconFinder()
        favicon_parser.feed(contents)
    except:
        pass

    # Another try block in case the parser throws an exception
    # AFTER finding the appropriate url.
    try:
        if favicon_parser.favicon_url:
            return favicon_parser.favicon_url
        else:
            url = '/'.join(url.split('/',3)[2:])
            root_directory = url.split('/')[0]
            favicon = httplib.HTTPConnection(root_directory)
            favicon.request('GET','/favicon.ico')
            response = favicon.getresponse()
            if response.status == 200:
                return 'http://%s/favicon.ico' % root_directory
            favicon = httplib.HTTPConnection('www.' + root_directory)
            favicon.request('GET','/favicon.ico')
            response = favicon.getresponse()
            if response.status == 200:
                return 'http://%s/favicon.ico' % ('www.' + root_directory)
    except:
        pass
    return None

import requests
import urllib
import re
from urllib.parse import urlparse, urljoin, unquote
import cgi
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import ssl

class Adapter(HTTPAdapter):
    
    def init_poolmanager(self, conn, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=conn,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

class URL:

    def __init__(self, url, verify=None, headers=None):
        self.url = url
        self.content_type = None
        self.filename = None
        self.response = None
        self.headers = headers
        self.final_url = url
        self.verify = verify
        self.status_code = None

    def __repr__(self):
        return self.url

    def get_headers_(self, url, headers, verify):
        
        print("Connecting to {0} ...".format(url))
        self.final_url = url
        
        if urlparse(url).scheme == "https":
            s = requests.Session()
            s.mount("https://", Adapter())
            self.response = s.get(url, headers=headers, verify=verify)
            self.status_code = self.response.status_code
        
        else:   
            self.response = requests.head(url, headers=headers)
            self.status_code = self.response.status_code
        
        if self.status_code // 100 == 2:
            try:
                self.content_type = cgi.parse_header(self.response.headers["content-type"])[0]
            except KeyError:
                r = requests.get(url, headers=headers, verify=verify)
                self.content_type = cgi.parse_header(r.headers["content-type"])[0]
            try:
                cd = self.response.headers["content-disposition"]
                _, params = cgi.parse_header(cd)
                self.filename = unquote(params['filename'])
            except KeyError:
                self.filename = (lambda x: unquote(urlparse(x).path.split("/")[-1])) (url)
            
            self.final_url = self.response.url
            
        elif self.status_code // 100 == 3:
            loc = self.response.headers['location']
            if urlparse(loc).scheme == "":
                loc = urljoin(url, loc)
            self.get_headers_(loc, headers, verify)

        else:
            request = urllib.request.Request(url)
            if headers != None:
                request.headers = headers
            r = urllib.request.urlopen(request, cafile=verify)
            self.status_code = r.status
            if self.status_code // 100 == 4:
                pass
            
            else:
                self.content_type = cgi.parse_header(r.getheader("Content-Type"))[0]
                try:
                    cd = r.getheader("Content-Disposition")
                    _, params = cgi.parse_header(cd)
                    self.filename = unquote(params['filename'])
                except (KeyError, TypeError):
                    self.filename = (lambda x: unquote(urlparse(x).path.split("/")[-1])) (url)

    def get_headers(self):
        print("--------------------------------------------------------------------------------")
        try:
            self.get_headers_(self.url, headers=self.headers, verify=self.verify)
        except Exception as e:
            self.filename, self.content_type = None, None
            print(e)
        print("Filename: {0}".format(self.filename))
        print("Type: {0}".format(self.content_type))
        print("Last URL: {0}".format(self.final_url))
        print("--------------------------------------------------------------------------------")
   
def href_filter(href):
    if href == "" or href == None:
        return None
    elif re.match("^javascript", href, re.IGNORECASE) != None:
        args = [x[1:-1] for x in re.findall('''"[^(,| )]+"|\'[^(,| )]+\'''', href)]
        for each in args:
            if urlparse(each).scheme in ["http", "https"]:
                return each
    elif urlparse(href).scheme == "mailto":
        return None
    elif urlparse(href).scheme == "" and urlparse(href).path == "" and urlparse(href).fragment != "":
        return None
    elif urlparse(href).scheme == "data":
        return href
    elif urlparse(href).scheme in ["http", "https"]:
        return href
    else:
        return None

if __name__ == "__main__":
    pass
   

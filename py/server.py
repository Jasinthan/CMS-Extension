from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from urllib.parse import urlparse
import time
import upload
import download
import urlcheck
import json
import re
import unicodedata
import base64img
import os
import sys
import ftplib

def ascii_normalize(s):
    nkfd_form = unicodedata.normalize('NFKD', s)
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii.decode('ascii')


def replace_unsupported_symbols(s):
    to_replace = [
        '\\\\',
        '\\',
        "\/",
        '/',
        "\:",
        "\*",
        "\<",
        "\>",
        "\|",
        ]
    return re.sub('|'.join(to_replace), '_', s)

def remove_front_trail(s):
    return re.sub("([\. ]+$|^ +)", "", s)


not_allowed_type = ['text/html', 'text/javascript', None]
hostName = 'localhost'
hostPort = 9000
page_info = None
dirlst = None
current_status = {'status': 'Ready'}
temp = '../temp'
headers_json = '../json/headers.json'
ftp_json = '../json/ftp.json'
cert_path = "../cert/cacert.pem"

#html = open('ui.html', 'r').read()
html = '''<html lang="en-US"><head> <script type="text/javascript" src="https://code.jquery.com/jquery-1.11.3.min.js"></script></head><body> <div id="editorExtension"> <style>#overlay{width: 580px; background-color: #D8D8D8; height: 233px; font-size: 120%; color: #444444; text-align: center; line-height: 233px; float: left; margin-bottom: -250px; position: relative; z-index: 1; -webkit-touch-callout: none; -webkit-user-select: none; -khtml-user-select: none; -moz-user-select: none; -ms-user-select: none; user-select: none; cursor: default;}#scrollBox{height: 200px; overflow: auto; width: 580px; background-color: black;}#extensionFooter{border: none;}.status{width: 15%; text-align: right;}.URLBox{width: 64%;}.linktext{width: 15%; float: left;}div[class="rowBox"] > input{background-color: transparent; color: white; padding: 5px; font-family: consolas; font-size: 80%; position: relative; border: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis ellipsis; -o-text-overflow: ellipsis;}div[id="extensionFooter"] > button{width: 65px}</style> <table class="tbl" style="width:580px"> <tbody> <tr> <td class="tbl_header"> <label>Extension</label> </td><tr/> <tr> <td> <div id="overlay"><font face="consolas">Switch to HTML mode to enable this feature.</font></div><div id="scrollBox"> </div></div></td></tr><tr> <td> <div id="extensionFooter" style="padding:5px"> <button type="button" id="loadBtn">Load</button>&nbsp; <button type="button" id="stripBtn" disabled>Strip</button>&nbsp; <button type="button" id="startBtn" disabled>Start</button>&nbsp; </div></td><tr> </tbody> </table> </div></body></html>'''

# FTP credentials

if os.path.exists(ftp_json):
    try:
        with open(ftp_json, 'r') as f:
            ftp_json = json.loads(f.read())
    except ValueError:
        sys.exit('ftp.json is invalid. Please check your syntax.')
else:
    sys.exit('Cannot find ftp.json.')

# Optional headers

request_headers = None

if os.path.exists(headers_json):
    with open(headers_json, 'r') as f:
        try:
            request_headers = json.loads(f.read())
        except ValueError:
            sys.exit('headers.json is invalid. Please check your syntax.')


# Make a threaded HTTP server

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):

    pass


class Handler(BaseHTTPRequestHandler):

    def allow_CORS(self):
        self.send_header('Content-type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods',
                         'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers',
                         'x-requested-with')
        self.end_headers()

    def send_data(self, data):
        self.wfile.write(bytes(json.dumps(data), 'utf-8'))
        
    def do_HEAD(self):
        self.send_response(200)
        self.allow_CORS()
        self.end_headers()
        print (time.asctime(), 'Connected to browser')

    def do_GET(self):

        if self.path == '/':
            try:
                self.send_response(200)
                self.allow_CORS()
                self.end_headers()
                self.wfile.write(bytes(html, 'utf-8'))
                print (time.asctime(), 'Editor UI loaded')
#                print (time.asctime(),
#                       'Client {0} accessed {1}'.format(str(self.client_address[0]) + ":" + str(self.client_address[1]),
#                       self.path))
            except IOError:
                self.send_error(404)
        elif self.path == '/status':

            self.send_response(200)
            self.allow_CORS()
            self.send_data(current_status)
        else:

            self.send_response(404)

    def log_message(self, format, *args):
        return

    def do_POST(self):
        global current_status
        global dirlst
        global page_info
        global upl

        self.send_response(200)
        self.allow_CORS()

        length = int(self.headers['Content-Length'])
        self.post_data = self.rfile.read(length)  # bytes
        #print(self.post_data.decode('utf-8'))
        recv = json.loads(self.post_data.decode('utf-8'))

        if type(recv) == dict:
            if 'PAGEINFO' in recv:
                page_info = recv['PAGEINFO']
                print (time.asctime(), 'Page info loaded')
            elif 'START' in recv:

                # try:

                try:
                    url = recv['START']['URL']
                except KeyError:
                    url = None

                tag_name = recv['START']['tagName']

                try:
                    new_dirlst = [page_info['prod'],
                              page_info['serverFolder'], (lambda t: \
                              ('File' if t == 'A' else 'Image'
                              ))(tag_name)] + list(map(lambda x: \
                        remove_front_trail(ascii_normalize(replace_unsupported_symbols(x))),
                        page_info['pageList']))
                except TypeError:
                    print("Cannot retrieve server number. You need to re-login into the CMS site.")
                    sys.exit()

                            # Check URL

                current_status = {'status': 'Checking'}

                URL = urlcheck.href_filter(url)

                if URL == None:
                    current_status = {'status': 'Skipped', 'URL': URL}
                else:

                                # Base64 img case:

                    if urlparse(URL).scheme == 'data':
                        filename = base64img.save_to_file(URL,
                                directory=temp)

                        current_status = {'status': 'Uploading'}
                        if new_dirlst != dirlst:
                            dirlst = new_dirlst
                            upl.jump(dirlst)

                        while True:
                            try:
                                upl.upload(filename, directory=temp)
                            except ftplib.all_errors:
                                print (time.asctime(),
                                        'Failed to upload {0}. Retrying.'.format(filename))
                                upl = upload.Upload()
                                upl.login(ftp_json['server'], user=ftp_json['username'],
          pswd=ftp_json['password'])
                                upl.jump(dirlst)
                                upl.upload(filename, directory=temp)
                            break

                        URL = '/UserFiles/Servers/' \
                            + '/'.join(dirlst[1:]) + '/' + filename
                        current_status = {'status': 'Done', 'URL': URL}
                    else:

                                # Non-Base64 img case:

                        chk = urlcheck.URL(URL, headers=request_headers, verify=cert_path)
                        chk.get_headers()

                        if chk.content_type in not_allowed_type \
                            or chk.filename == None:
                                if chk.status_code != None:
                                    if chk.status_code // 100 == 4:
                                        current_status = {'status': 'Error ' + str(chk.status_code),
                                    'URL': URL}
                                        
                                    else:
                                        current_status = {'status': 'Skipped',
                                    'URL': URL}
                                    
                                else:
                                    current_status = {'status': 'Error'}
                        else:

                                        # Download

                            current_status = {'status': 'Downloading'}
                            filename = chk.filename
                            download.get_file(chk.final_url,
                                    fname=chk.filename, directory=temp,
                                    headers=request_headers,
                                    verify=cert_path)

                                        # Upload

                            current_status = {'status': 'Uploading'}
                            if new_dirlst != dirlst:
                                dirlst = new_dirlst
                                upl.jump(dirlst)

                            while True:
                                try:
                                    upl.upload(filename, directory=temp)
                                except ftplib.all_errors:
                                    print (time.asctime(),
        'Re-uploading {0} ...'.format(filename))
                                    upl = upload.Upload()
                                    upl.login(ftp_json['server'], user=ftp_json['username'],
              pswd=ftp_json['password'])
                                    upl.jump(dirlst)
                                    upl.upload(filename, directory=temp)
                                break

                            URL = '/UserFiles/Servers/' \
                                + '/'.join(dirlst[1:]) + '/' + filename
                            current_status = {'status': 'Done',
                                    'URL': URL}
            else:

                    # except:
                    # current_status = {"status": "Error"}

                pass


if __name__ == '__main__':
    server = ThreadedHTTPServer((hostName, hostPort), Handler)
    print (time.asctime(), 'Server starts - %s:%s' % (hostName,
           hostPort))

    # Create an object that handles uploads

    try:
        upl = upload.Upload()
        upl.login(ftp_json['server'], user=ftp_json['username'],
              pswd=ftp_json['password'])
    except Exception as e:
        print(e)
        sys.exit

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    upl.logout()
    server.server_close()
    print (time.asctime(), 'Server stops - %s:%s' % (hostName,
           hostPort))		
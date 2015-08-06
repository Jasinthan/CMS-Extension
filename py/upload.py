from ftplib import FTP
import time
import os

class Upload:
    
    def __init__(self):
        self.ftp = None
        self.server = None
        self.user = None
        self.pswd = None

    def login(self, server, user="anonymous", pswd=""):
        self.ftp = FTP(server)
        self.ftp.login(user=user, passwd=pswd)
        self.server = server
        self.user = user
        self.pswd = pswd
        print(time.asctime(), "Successfully connected to %s" % self.server)

    def logout(self):
        self.ftp.quit()
        print(time.asctime(), "Disconnected from %s" % self.server)

    def upload(self, fname, directory=""):
        print(time.asctime(), "Uploading " + fname + " ...")
        self.ftp.storbinary("STOR " + fname, open(os.path.join(directory, fname), "rb"))
        print(time.asctime(), fname + " has been uploaded.")
    
    def dir_exists(self, dirname):
        for entry in tuple(self.ftp.mlsd()):
            name = entry[0]
            info = entry[1]
            if info["type"] == "dir":
                if dirname == name:
                    return True
        return False

    def mkdirs(self, dirlst):
            if dirlst == []:
                pass
            else:
                folder = dirlst[0]
                rest = dirlst[1:]
                if self.dir_exists(folder):
                    self.ftp.cwd(folder)
                    self.mkdirs(rest)
                else:
                    self.ftp.mkd(folder)
                    self.ftp.cwd(folder)
                    self.mkdirs(rest)

    def jump(self, dirlst):
        self.ftp.cwd("/")
        self.mkdirs(dirlst)
        self.ftp.dir()
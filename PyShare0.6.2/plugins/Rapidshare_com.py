# Rapidshare Uploader v 1.1 by Adam Poit
#
# Type these commands from the command line to use this script:
#
# python rsupload.py myfile.rar free (Uploads to rapidshare as a free user)
# python rsupload.py myfile.rar col Username Password (Uploads to a rapidshare collectors account)
# python rsupload.py myfile.rar prem Username Password (Uploads to a premium account)
#
# To upload multiple files, separate them with a # (number sign). Like this:
#
# python rsupload.py myfile.rar#anotherfile.rar#onemore.rar prem Username Password
#
# At the end, RSUploader will save all the urls to rsurls.txt
#################################################################
# project site <http://code.google.com/p/python-rapidshare-upload/> indicates that this script is GPL v 3
# I modiffied it to use with PyShare <https://launchpad.net/pyshare>  . <Sebastian Kacprzak> <naicik |at| gmail |dot| com>

from threading import Thread
from AbstractPlugin import AbstractPlugin
import socket
import re
from hashlib import md5
from threading import BoundedSemaphore
from libs.uploadHelper import createLinks
from libs.cliHelper import printLink, printProgressToCLI

class Rapidshare_com(AbstractPlugin):
    NAME = "Rapidshare"
    ACCEPTED_FILE_TYPES = "*"
    CAN_USE_PASSWORD = True
    PASSWORD_REQUIRED = False

    def upload(self, file, callbackFunction, username, password):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("rapidshare.com", 80))

        uls = sock.send('GET /cgi-bin/rsapi.cgi?sub=nextuploadserver_v1 HTTP/1.0\r\n\r\n')
        uploadserver = str(uls)
        sock.close()

        f = open(file)
        filecontent = f.read()
        size = len(filecontent)
        md5hash = md5(filecontent)
        f.close()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("rs" + uploadserver + "l3.rapidshare.com", 80))

        boundary = "---------------------632865735RS4EVER5675865"
        contentheader = boundary + "\r\nContent-Disposition: form-data; name=\"rsapi_v1\"\r\n\r\n1\r\n"

        if username:
#            if type == "prem":
            contentheader += boundary + "\r\nContent-Disposition: form-data; name=\"login\"\r\n\r\n" + username + "\r\n"
            contentheader += boundary + "\r\nContent-Disposition: form-data; name=\"password\"\r\n\r\n" + password + "\r\n"

#            if type == "col":
#                contentheader += boundary + "\r\nContent-Disposition: form-data; name=\"freeaccountid\"\r\n\r\n" + username + "\r\n"
#                contentheader += boundary + "\r\nContent-Disposition: form-data; name=\"password\"\r\n\r\n" + password + "\r\n"

        contentheader += boundary + "\r\nContent-Disposition: form-data; name=\"filecontent\"; filename=\"" + file + "\"\r\n\r\n"
        contenttail = "\r\n" + boundary + "--\r\n"
        contentlength = len(contentheader) + size + len(contenttail)

        header = "POST /cgi-bin/upload.cgi HTTP/1.1\r\nHost: rs" + uploadserver + ".rapidshare.com\r\nContent-Type: multipart/form-data; boundary=" + boundary + "\r\nContent-Length: " + str(contentlength) + "\r\n\r\n" + contentheader

        sock.send(header)

        f = open(file)

        bufferlen = 0
        while True:
            chunk = f.read(64000)
            if not chunk:
                break
            sock.send(chunk)
            bufferlen += len(chunk)
            self.progress(0,0,upload_t = size, upload_d = bufferlen)
          
        sock.send(contenttail)

        result = sock.recv(1000000)
        f.close()
        sock.close()

        newhash = re.search('File1.4=(\w+)', result)
        oldhash = "File1.4=" + md5hash.hexdigest().upper()
        if not newhash:
            raise Exception("Upload unsuccessful")
        if newhash.group() == oldhash:
            upload = re.search('File1.1=(\S+)', result)
            link = upload.group()[8:]#Cut'File1.1='
            links = createLinks(link, file)
            callbackFunction(links, self.file_number, file)
        else:
            raise Exception("Upload unsuccessful")


def uploadFile(file, resultCallbackFunction=printLink, progressCallbackFunction=printProgressToCLI, file_number = 0, semaphore = BoundedSemaphore(2), username="", password=""):
    rs = Rapidshare_com(file, resultCallbackFunction, progressCallbackFunction, file_number)
    from Settings import Settings
    set = Settings()
    if set.getUseRSPassword():
        username,password = set.getRSCredentials()
    rs.upload(semaphore, username, password)
    del username
    del password


def uploadFiles(files, resultCallbackFunction=printLink, progressCallbackFunction=printProgressToCLI, file_number = 0, semaphore = BoundedSemaphore(2), username="", password=""):
    for file in files:
        rs = Rapidshare_com(file, resultCallbackFunction, progressCallbackFunction, file_number)
        file_number += 1
        t = Thread(None, rs.upload, None,(semaphore, username, password))
        t.start()
           
        

if __name__ == "__main__":
    import sys
    filename = sys.argv[1]
    type = sys.argv[2]
    username = password = ""
    if type != "free":
        username = sys.argv[3]
        password = sys.argv[4]

    files = filename.split('#')

    for file in files:
        rs = Rapidshare_com(file,printLink,printProgressToCLI,0)
        rs.upload(BoundedSemaphore(), username, password)

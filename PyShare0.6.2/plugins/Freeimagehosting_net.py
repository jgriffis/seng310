#!/usr/bin/env python

# -*- coding: utf-8 -*-

#    Copyright (C) <2009>  <Sebastian Kacprzak> <naicik |at| gmail |dot| com>
#    Partial copyright <Balazs Nagy> <nxbalazs |at| gmail |dot| com> (few lines from his drop2imageshack plasma)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import gettext
gettext.bindtextdomain('sendToFreeimagehosting', '.')
gettext.textdomain('sendToFreeimagehosting')
_ = gettext.gettext

errorDialog = None

import pycurl
from threading import Thread
#import os
from StringIO import StringIO
from threading import BoundedSemaphore
from libs.uploadHelper import createLinks
from libs.BeautifulSoup import BeautifulSoup
from libs.cliHelper import printLink, printProgressToCLI
#from helpers.gnomeHelper import getMimeTypes
#from DB import DB
#db=DB()


acceptImageExtensions = ["jpg", "jpeg","png"]
def getAcceptedImageTypes():
    return acceptImageExtensions

def getReturnedLinkTypes():
    return ['IM', 'Forum', 'Alt Forum', 'HTML', 'Forum Thumb', 'Alt Forum Thumb', 'HTML Thumb']

def correctExtension(file):
    """checks if given string have a allowed extension"""
    #TODO: switch to checking mime types
    return file.split('.')[-1].lower() in acceptImageExtensions


class __Freeimagehosting():

    def __init__(self, fileNumber, progressCallbackFunction):
        self.fileNumber = fileNumber
        self.progressCallbackFunction = progressCallbackFunction


    def parseHTML(self, html):
        """parse given html
        returns dictionary with keys: IM, Forum, Alt Forum, HTML, Direct, Forum Thumb, Alt Forum Thumb, HTML Thumb, Twitter Link"""
        soup = BeautifulSoup(html)

        link=soup.find('table').findNext('table').findNext('table').tr.findNext('table').findNext('table').tr.td.a
        adLink=link['href']

        thumbLink=link.img['src']

        directhtmlinput=soup.find(attrs={'name' : 'directhtml'})
        alink=BeautifulSoup(directhtmlinput['value'])
        imageLink=alink.find('img')['src']

        links = createLinks(adLink, None, imageLink,thumbLink)

        return links, [imageLink, thumbLink, adLink]

    def progress(self, download_t, download_d, upload_t, upload_d):
        """passes self.fileNumber and arguments to self.progressCallbackFunction"""
        self.progressCallbackFunction(self.fileNumber, download_t, download_d, upload_t, upload_d)

    def upload(self, file, semaphore, callbackFunction):
        """can throw errors"""
        if not correctExtension(file): # usually this check is not needed, but it can help later in other script
            raise Exception(_("Invalid file extension\nYou can upload only ") + str(acceptImageExtensions), _("Invalid file extension"))
        curl = pycurl.Curl()

        curl.setopt(pycurl.URL, "http://www.freeimagehosting.net/upload.php")
        curl.setopt(pycurl.HTTPHEADER, ["Except:"])
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.HTTPPOST, [('attached', (pycurl.FORM_FILE, file))])

        buf = StringIO()
        curl.setopt(pycurl.WRITEFUNCTION, buf.write)
        curl.setopt(curl.NOPROGRESS, 0)
        curl.setopt(curl.PROGRESSFUNCTION, self.progress)

        semaphore.acquire()
        try:
            curl.perform()
        except pycurl.error:
            semaphore.release()
            raise Exception(_("""Upload unsuccessful :(
Few possible reasons:
-transmission error occured
-server is down
-your connection is down
-server didn't like your image(to big/wrong file type etc..)
-server blocked connection because of too many attempts.

Please try again later. If the problem still occur try sending file manually by website."""), _("Upload unsuccessful"))
        semaphore.release()
        links, basicLinks = self.parseHTML(buf.getvalue().strip()) # sometimes there are leading witespace in stream and minidom don't like them
        #db.addFile("Freeimagehosting",basicLinks[0], basicLinks[1], basicLinks[2], os.path.basename(file), os.path.getsize(file),file.split('.')[-1].lower(), getMimeTypes(file))
        callbackFunction(links,self.fileNumber,file)

def uploadFile(file, resultCallbackFunction=printLink, progressCallbackFunction=printProgressToCLI, fileNumber = 0, semaphore = BoundedSemaphore(2), username="", password=""):
    sti = __Freeimagehosting(fileNumber, progressCallbackFunction)
    sti.upload(file, semaphore, resultCallbackFunction)

def uploadFiles(files, resultCallbackFunction=printLink, progressCallbackFunction=printProgressToCLI, fileNumber = 0, semaphore = BoundedSemaphore(2)):
    """uploads given files in threads
    This function is non blocking, you should give a callback function as parameter if you want to know when it ended or what is the progress
    Error will be thrown if upload was unsuccessful"""
    threadList = []
    for file in files:
        sti = __Freeimagehosting(fileNumber, progressCallbackFunction)
        fileNumber += 1
        t = Thread(None, sti.upload, None,(file, semaphore, resultCallbackFunction))
        t.start()
        threadList.append(t)
    return threadList


if __name__ == "__main__":
    from sys import argv
    if len(argv) > 1:
        args = argv[1:] # first argument is file name, so ignore it
        threadList = uploadFiles(args)
        for thread in threadList:
            thread.join() # wait for all threads to end
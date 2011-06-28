#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2009,2011>  <Sebastian Kacprzak> <naicik |at| gmail |dot| com>

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

"""This module is supposed to make sure that plugins:
-don't crash the program
-errorCallback is called if anything bad happen
-plugins are running in their own threads
-log errors
-number of concurrent uploads is not exceeded

Do note that this module is not a security sandbox
(fe: malicious plugin stil can delete home folder)"""

from threading import Thread
from sys import exc_info
from plugins.libs.cliHelper import printLink, printProgressToCLI
from Settings import Settings

import logging
from helpers.gnomeHelper import getPyShareHomeDirectory
LOG_PATH = getPyShareHomeDirectory() + 'errorLog'
logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG)
logger1 = logging.getLogger('pluginWrapper')



def __runMethod(method, arguments,errorCallback,errorCallbackArgument):
    """runs method and catches all exceptions
    errorCallback function will be called if Exception occurs"""
    try:
        apply(method, arguments)
    except:
        excInfo = exc_info()
        logger1.exception(excInfo[1])
        errorCallback(errorCallbackArgument)

def runMethodInThread(method,arguments,errorCallback,errorCallbackArgument):
    """runs method in new thread
    errorCallback function will be called if Exception occurs"""
    t = Thread(None, __runMethod, None,(method, arguments,errorCallback,errorCallbackArgument))
    t.start()
    return t

def uploadFiles(Uploader, errorCallback,
    files, resultCallbackFunction, progressCallbackFunction, fileNumber, semaphore, username="", password=""):
    """uploads files with given uploader, each file in new thread
    each thread would be given incremented fileNumber
    returns: list of started threads
    errorCallback function will be called if Exception occurs"""
    threadList = []
    for file in files:
        t = runMethodInThread(__createUploaderInstanceAndUploadFile,
            (Uploader, file, semaphore,
            username, password,
            resultCallbackFunction, progressCallbackFunction,
            fileNumber),
        errorCallback,
        fileNumber)
        threadList.append(t)
        fileNumber += 1
    return threadList

def uploadFile(Uploader, errorCallback,
    file, resultCallbackFunction, progressCallbackFunction, fileNumber, semaphore, username="", password=""):
    """uploads file with given uploader
    errorCallback function will be called if Exception occurs"""
    t = runMethodInThread(__createUploaderInstanceAndUploadFile,
        (Uploader, file, semaphore,
            username, password, 
            resultCallbackFunction, progressCallbackFunction,
            fileNumber),
        errorCallback,
        fileNumber)
    return t

def __createUploaderInstanceAndUploadFile(Uploader, file, semaphore,
    username, password,
    resultCallbackFunction=printLink, progressCallbackFunction=printProgressToCLI,
    fileNumber = 0):
    uploader = Uploader(fileNumber, progressCallbackFunction)
    credentials = Settings().getUploaderCredentials(uploader.NAME)
    if credentials:
        username, password = credentials
    semaphore.acquire()
    try:
        uploader.upload(file, resultCallbackFunction, username, password)
    finally:
        semaphore.release()



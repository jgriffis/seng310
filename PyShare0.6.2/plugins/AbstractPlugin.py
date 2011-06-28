#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Define API for plugins"""

#    Copyright (C) <2011>  <Sebastian Kacprzak> <naicik |at| gmail |dot| com>

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

__author__="Sebastian Kacprzak <naicik at gmail.com>"
__date__ ="$2011-01-22 17:11:03$"

class AbstractPlugin():
    """Suggested superclass for all plugins

    It defines simple constructor and progress method
    that takes care of informing callback about upload status.

    Do note that upload method have to be overriden.
    It is included in this class only as a information
    for programmers about parameters and expected functionality
    of methods that overrides it.
    
    Fields NAME, ACCEPTED_FILE_TYPES and CAN_USE_PASSWORD are
    also required.

    """
    # unique name of the plugin. Name of the site is advised
    NAME = None # fe: example.com
    # file types accepted by hosting
    # if site accept all filetypes use "*"
    ACCEPTED_FILE_TYPES = None # fe: ["png","jpg"]
    # can plugin send files to user account
    CAN_USE_PASSWORD = None # fe: False
    # is username and password required for sending
    PASSWORD_REQUIRED = None # fe: False

    def __init__(self, file_number, progress_callback_function):
        """store values for callback"""
        self.file_number = file_number
        self.progress_callback_function = progress_callback_function

    def progress(self, download_t, download_d, upload_t, upload_d):
        """call this function to inform about upload progress

        passes self.file_number and arguments to self.progressCallbackFunction
        upload_t - total size to be uploaded
        upload_d - total size already uploaded
        download_t - currently ignored - added to fit pycurl format
        download_d - currently ignored - added to fit pycurl format

        """
        self.progress_callback_function(self.file_number, download_t, download_d, upload_t, upload_d)

    def upload(self, file, callbackFunction, username = None, password = None):
        """Upload file, and pass links to callbackFunction.

        Optionaly call self.progress periodically to inform about upload status
        file - path to file that should be uploaded
        callbackFunction - function that should be informed about result

        """
        raise Exception("This method should be overriden")


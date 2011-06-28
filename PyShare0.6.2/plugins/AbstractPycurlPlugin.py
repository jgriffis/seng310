#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
__date__ ="$2011-01-22 18:43:31$"

from AbstractPlugin import AbstractPlugin
import pycurl
from StringIO import StringIO
from plugins.libs.pycurlHelper import getPycurlProxyAuthenticationType
from Settings import Settings
from tempfile import mktemp
set = Settings()


class AbstractPycurlPlugin(AbstractPlugin):
    """Suggested superclass for plugins using pycurl for uploading

    This class takes care of common operation, that
    are needed to upload files by pycurl.
    Always override parseResponse and upload methods

    """

    def _setCurlProxyOpts(self, curl):
        """sets proxy settings to curl if needed"""
        if(set.getUseProxy()):
            curl.setopt(pycurl.PROXY, set.getProxyName())
            curl.setopt(pycurl.PROXYPORT, set.getProxyPort())
            credentials = set.getProxyCredentials()
            if credentials:
                user_name_and_password = credentials[0] + ":" + credentials[1]
                curl.setopt(pycurl.PROXYUSERPWD, user_name_and_password)
                del user_name_and_password
                del credentials
            curl.setopt(pycurl.PROXYAUTH, getPycurlProxyAuthenticationType())

    def uploadUsingPycurlPost(self, file, callback_function, URL, POST):
        """uploads file using pycurl POST

        proxy settings are taken care of
        callback function is called after upload
        URL - URL that should be called
        POST - post arguments as a list fe: [('fileupload', (pycurl.FORM_FILE, file)), ('xml', 'yes')]
        
        """

        curl = pycurl.Curl()

        curl.setopt(pycurl.URL, URL)
        self._setCurlProxyOpts(curl)
        curl.setopt(pycurl.POST, 1)
        curl.setopt(pycurl.HTTPPOST, POST)
        curl.setopt(pycurl.FOLLOWLOCATION, 1)
#        cookie_file_name = mktemp()
#        curl.setopt(pycurl.COOKIEFILE, cookie_file_name)
#        curl.setopt(pycurl.COOKIEJAR, cookie_file_name)
#        curl.setopt(pycurl.HEADER,1)

        buf = StringIO()
        curl.setopt(pycurl.WRITEFUNCTION, buf.write)
        curl.setopt(curl.NOPROGRESS, 0)
        curl.setopt(curl.PROGRESSFUNCTION, self.progress)

        result = curl.perform()
        response = buf.getvalue().strip()
        try:
            links = self.parseResponse(response, file)
        except IndexError:
             raise Exception("error uploading file: " + str(file) + "\n" + response)
        callback_function(links, self.file_number, file)


    def parseResponse(self, response, fileName):
        """Parse response returned by pycurl.

        Returns all links provided by hosting site,
        This method have to be overridden.

        """
        raise Exception("This method should be overriden")


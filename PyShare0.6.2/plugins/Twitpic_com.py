#    Copyright (C) <2011>  <Sebastian Kacprzak> <naicik |at| gmail |dot| com>
#    Copyright (C) <2010>  @silvio1964 http://ubuntubond.blogspot.com
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
__date__ ="$2011-01-22 17:00:56$"

from AbstractPycurlPlugin import AbstractPycurlPlugin
from pycurl import FORM_FILE
from xml.dom import minidom
from StringIO import StringIO
from libs.uploadHelper import createLinks

class Twitpic_com(AbstractPycurlPlugin):
    ACCEPTED_FILE_TYPES = ["jpg", "bmp", "gif", "png", "tif"]
    NAME = "Twitpic"
    CAN_USE_PASSWORD = True
    PASSWORD_REQUIRED = True

    def upload(self, file, callbackFunction, username, password):
        """Uploads file, and passed links to callbackFunction.
        Optionaly this method may call self.progress to inform about upload status"""
        self.uploadUsingPycurlPost(file, callbackFunction,
            "http://twitpic.com/api/upload",
             [('media', (FORM_FILE, file)), ('username', username), ('password',password)])

    def parseResponse(self, response, fileName):
        xmldoc = minidom.parse(StringIO(response))

        uploadSuccessful = xmldoc.getElementsByTagName("rsp")[0].getAttribute("stat") == 'ok'

        if not uploadSuccessful:
            err = xmldoc.getElementsByTagName("err")[0]
            code = err.getAttribute("code")
            msg = err.getAttribute("msg")
            raise Exception("Error: " + msg + " (" + code + ")")

        #links = {"IM":xmldoc.getElementsByTagName("mediaurl")[0].firstChild.data}
        link = xmldoc.getElementsByTagName("mediaurl")[0].firstChild.data
        links = createLinks(link, fileName)
        return links


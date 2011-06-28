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
__date__ ="$2011-02-15 19:10:02$"

from AbstractPycurlPlugin import AbstractPycurlPlugin
from pycurl import FORM_FILE
import pycurl
import StringIO
from libs.uploadHelper import createLinks

class Imgur_com(AbstractPycurlPlugin):
    ACCEPTED_FILE_TYPES = ["jpg", "bmp", "gif", "png", "tif", "pdf", "xcf", "apng"]
    NAME = "Imgur"
    CAN_USE_PASSWORD = True
    PASSWORD_REQUIRED = True

    def login(self, username, password):
        cookie_file_name = "/tmp/imagurcookie"

        if (username!="" and password!=""):
                #print "Trying to login"
                l=pycurl.Curl()
                loginData = [ ("username", username),("password", password), ("submit", "Continue") ]
                l.setopt(l.URL, "http://imgur.com/signin")
                l.setopt(l.HTTPPOST, loginData)
                #l.setopt(l.USERAGENT,"User-Agent: Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.4) Gecko/20091028 Ubuntu/9.10 (karmic) Firefox/3.5.1")
                l.setopt(l.FOLLOWLOCATION,1)
                l.setopt(l.COOKIEFILE,cookie_file_name)
                l.setopt(l.COOKIEJAR,cookie_file_name)
                l.setopt(l.HEADER,1)
                loginDataReturnedBuffer = StringIO.StringIO()
                l.setopt( l.WRITEFUNCTION, loginDataReturnedBuffer.write )



                loginDataReturned = loginDataReturnedBuffer.getvalue()
                l.close()




    def upload(self, file, callbackFunction, username, password):
        """Uploads file, and passed links to callbackFunction.
        Optionaly this method may call self.progress to inform about upload status"""
        self.login(username, password)
        self.uploadUsingPycurlPost(file, callbackFunction,
            #"http://imgur.com/signin",
            #"http://api.imgur.com/2/upload.xml",
            "http://imgur.com/api/upload.xml",
             #[("image", (FORM_FILE, file)), ("username",username), ("password", password), (("key", "e85c0044b9222bc9a2813679a452f54f"))])
             [("image", (FORM_FILE, file)), (("key", "e85c0044b9222bc9a2813679a452f54f"))])

    def parseResponse(self, response, fileName):
        #print response
        """<rsp stat="ok"><image_hash>o03Rj</image_hash><delete_hash>9PkXVHJf7h7Ax4b</delete_hash><original_image>http://i.imgur.com/o03Rj.jpg</original_image><large_thumbnail>http://i.imgur.com/o03Rjl.jpg</large_thumbnail><small_thumbnail>http://i.imgur.com/o03Rjs.jpg</small_thumbnail><imgur_page>http://imgur.com/o03Rj</imgur_page><delete_page>http://imgur.com/delete/9PkXVHJf7h7Ax4b</delete_page></rsp>"""

        tag = "<original_image>"
        link_start = response.find(tag)
        if link_start < 0:
            raise Exception("Upload failed " + response)
        link_end = response.find("</original_image>")

        tag = "<imgur_page>"
        link_start = response.find(tag)
        if link_start < 0:
            raise Exception("Upload failed " + response)
        link_end = response.find("</imgur_page>")
        
        link = response[link_start + len(tag): link_end]
        links = createLinks(link, fileName)
        return links


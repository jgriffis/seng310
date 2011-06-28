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


from AbstractPycurlPlugin import AbstractPycurlPlugin
from pycurl import FORM_FILE
from StringIO import StringIO
from xml.dom import minidom
from libs.uploadHelper import createLinks

class Imageshack_us(AbstractPycurlPlugin):
    NAME = "Imageshack"
    ACCEPTED_FILE_TYPES = ["jpg", "bmp", "gif", "png", "tif"]
    CAN_USE_PASSWORD = True
    PASSWORD_REQUIRED = False

    def parseResponse(self, xml, fileName = None):
        """find links in given xml

        return dictionary with keys: IM, Forum, Alt Forum, HTML, Direct, Forum Thumb, Alt Forum Thumb, HTML Thumb, Twitter Link

        """
        xmldoc = minidom.parse(StringIO(xml))

        imageLink = xmldoc.getElementsByTagName("image_link")[0].firstChild.data 
        thumbLink = xmldoc.getElementsByTagName("thumb_link")[0].firstChild.data 
        adLink = xmldoc.getElementsByTagName("ad_link")[0].firstChild.data 
        thumbExists = xmldoc.getElementsByTagName("thumb_exists")[0].firstChild.data 
        if thumbExists == "no":
            thumbLink = imageLink # thumb was not generated, use image as a thumb
        links = createLinks(adLink, None, imageLink,thumbLink)
        return links#, [imageLink, thumbLink, adLink]

    def __changePngExtensionIfNeeded(self, file):
        """copies png files to temporary file with jpg extension

        workaround for imageshack failing to accept png
        https://bugs.launchpad.net/pyshare/+bug/587255

        """
        if file.split('.')[-1].lower() == "png":
            # imports are embed to make it easier to delete
            # workaround when its no longer needed
            from tempfile import mktemp
            tempName = mktemp(".jpg")
            from shutil import copyfile
            copyfile(file, tempName)
            file = tempName
        return file
    
    def upload(self, file, callbackFunction, username, password):
        """Upload file to imageshack. Username and password is used if given"""

        file = self.__changePngExtensionIfNeeded(file)
        post =  [('fileupload', (FORM_FILE, file)),  ('xml', 'yes')]
        if username:
            post.append(('a_username', username))
            post.append(('a_password', password))
        self.uploadUsingPycurlPost(file, callbackFunction,
            "http://www.imageshack.us/index.php",
            #"http://www.imageshack.us/upload_api.php", #returns more info, that we don't need
            post)




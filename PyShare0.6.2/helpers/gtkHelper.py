#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2010>  <Sebastian Kacprzak> <naicik |at| gmail |dot| com>

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
__date__ ="$2010-03-11 18:19:58$"

import gtk
import os
from hashlib import md5
#from glib import GError
import gnomevfs
from gnomeHelper import getPyShareHomeDirectory
from Settings import Settings
set = Settings()

def createCombobox(linkNames=None):
    """returns comobox with entries from given linkNames"""
    comboBox = gtk.combo_box_new_text()
    if linkNames:
        populateCombobox(comboBox,linkNames)
    return comboBox

def populateCombobox(comboBox, linkNames):
    for name in linkNames:
        comboBox.append_text(name)

def copyToClipBoard(widget, text):
    display = gtk.gdk.display_manager_get().get_default_display()
    clipboard = gtk.Clipboard(display, set.getClipboardType())
    clipboard.set_text(text)

def getMimeTypes(file):
    mime = gnomevfs.get_mime_type(file)
    return mime

def isImage(mimeType):
    if mimeType.split('/')[0].lower() == "image":
        return True
    else:
        return False

def __getPixbufFromGnomeIcons(mimeType,size):
    #TODO: swtich to using gio when hardy get depraceted
    iconsPath = "/usr/share/icons/gnome/32x32/mimetypes/"
    defaultIcon = iconsPath + "empty.png"

    iconName = "gnome-mime-"+mimeType.split('/')[0].lower()+"-"+mimeType.split('/')[-1].lower()+".png"
    scalableIconPath = "/usr/share/icons/gnome/scalable/mimetypes/" + iconName
    if os.path.exists(scalableIconPath):
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(scalableIconPath,size,size)
    elif os.path.exists(iconsPath+iconName):
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(iconsPath+iconName,size,size)
    else:
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(defaultIcon,size,size)
    return pixbuf

def createThumbnail(file):
    """takes file url as parameter, returns thumbnail without changing image ratio"""
    #image = gtk.Image()
    #get pixbuf from file or from system icon
    thumbnailSize = set.getThumbnailSize()
    try:
        originalPixbuf = gtk.gdk.pixbuf_new_from_file(file)
        #scale pixbuf
        ratio = float(originalPixbuf.get_width()) / originalPixbuf.get_height()
        thumbnailSizeY = thumbnailSizeX = thumbnailSize
        if ratio > 1:
            thumbnailSizeY /= ratio
        else:
            thumbnailSizeX *= ratio
        pixbuf = originalPixbuf.scale_simple(int(thumbnailSizeX), int(thumbnailSizeY), gtk.gdk.INTERP_BILINEAR)
        #image.set_from_pixbuf(pixbufZoomed)
    #except GError:
        #print "create thumbnail from mime type"
    except: #GError cannot be imported in some system, fe: Ubuntu Hardy Haron
        pixbuf = __getPixbufFromGnomeIcons(getMimeTypes(file),thumbnailSize)
    
    return pixbuf

def saveThumbnail(pixbuf, file, link):
    cachePath = getPyShareHomeDirectory() + 'cache/'
    if not os.path.exists(cachePath):
            os.makedirs(cachePath)
    filename = cachePath + md5(link).hexdigest()
    splittedFileName = file.split('.')
    ext = None
    if len(splittedFileName) > 1:
        ext = splittedFileName[-1].lower()
    if(ext=="jpg" or ext=="gif" or (not ext)):
        pixbuf.save(filename, "jpeg")
    else:
        pixbuf.save(filename, ext)

def getThumbnailFromCache(link):
    cachePath = getPyShareHomeDirectory() + 'cache/'
    filename = cachePath + md5(link).hexdigest()
    if os.path.exists(filename):
        pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
    else:
        pixbuf = None
    return pixbuf

def removeFromCache(link):
    cachePath = getPyShareHomeDirectory() + 'cache/'
    filename = cachePath + md5(link).hexdigest()
    if os.path.exists(filename):
        os.remove(filename)
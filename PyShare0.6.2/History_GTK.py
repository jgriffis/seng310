#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2009>  <Krzysztof Chrobak> <krzycho |dot| ch |at| gmail |dot| com>

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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

import gettext
import urllib
from hashlib import md5
import os

#gettext.bindtextdomain('HistoryWindow', '.')
#gettext.textdomain('HistoryWindow')
#_ = gettext.gettext

try:
    translationsDomainName = 'History_GTK'
    translationsDirName = 'translations'
    translation = gettext.translation(translationsDomainName,translationsDirName)
    _ = translation.gettext
except IOError:
    def return_english(text):
        return text
    _ = return_english
    print "translations for your language don't yet exist"

#gettext.install(translationsDomainName, translationsDirName)

#from PyShare_GTK import importErrorDialog as errorDialog
from DB import DB
from Settings import Settings
set = Settings()
from helpers.gnomeHelper import getPyShareHomeDirectory
from helpers.gtkHelper import createCombobox, isImage, getThumbnailFromCache, copyToClipBoard, removeFromCache
from helpers.conversionHelper import convert_date, convert_bytes
from plugins.libs.uploadHelper import createLinks

#try:
import pygtk
pygtk.require('2.0') # comboboxes needs pygtk 2.4 or higher, however they work fine with package 2.14.1-1ubuntu1 - probably version number differs..
import gtk
#except ImportError:
#    errorDialog(_("This script needs gtk and pygtk 2.0 or higher"))
#except AssertionError:
#    errorDialog(_("This script needs pygtk 2.0 or higher"))

#try:
#except ImportError, error:
#    errorDialog(error)

class History_GTK:
    db=DB()
    links = []
    elements = {}
    totalNumberOfElements = 0
    fileNumber = 0 

    def __init__(self, caller = None):
        self.__parent = caller
        self.window = gtk.Dialog("History", self.__parent, gtk.DIALOG_NO_SEPARATOR | gtk.DIALOG_MODAL)
        
        icon_theme = gtk.icon_theme_get_default()
        iconSize = 16
        
        try:
            pixbuf = icon_theme.load_icon("clock", iconSize, 0)
            self.window.set_icon(pixbuf)
        except:
            pass
        self.window.set_title(_("History"))
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_NORMAL)
        self.window.set_resizable(True)
        self.window.set_position(gtk.WIN_POS_CENTER)

        self.window.connect("destroy", self.__destroy)
        self.window.set_border_width(0)
        self.window.set_default_size(640, 480)

        self.treestore = gtk.TreeStore(str)

        root = self.treestore.append(None, [_('History')])
        hosting_root = self.treestore.append(None, [_('Hostings')])
        hostings_list=self.db.getHostingList()
        #get upload date
        upload_date_list=self.db.getUploadDate()

        for date_group in upload_date_list:
            piter = self.treestore.append(root, ['%s' % date_group[0]])
            hosting_by_date=self.db.getHostingListByDate(date_group[0])
            for hosting in hosting_by_date:
                self.treestore.append(piter, ['%s' % hosting[0] ])

        for hosting in hostings_list:
                self.treestore.append(hosting_root, ['%s' % hosting[1] ])
        
        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)
        self.treeview.add_events(gtk.gdk.BUTTON_PRESS_MASK )
        self.treeview.connect('row-activated', self.updatePanel)

        # create the TreeViewColumn to display the data
        self.tvcolumn = gtk.TreeViewColumn(_('History'))
        #self.tvcolumn.set_resizable(True)

        # add tvcolumn to treeview
        self.treeview.append_column(self.tvcolumn)
        self.tvcolumn.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        
        self.treeview.columns_autosize()

        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()

        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)

        #add mainbox to window
        mainbox = self.window.vbox
        #mainbox.show()
        #self.window.add(mainbox)
        
        #add horizontal paned to mainbox
        self.hpaned=gtk.HPaned()
        mainbox.pack_start(self.hpaned, True, True, 0)

        #add scrollbars to the treeview
        scrolltree = gtk.ScrolledWindow()
        scrolltree.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolltree.show()
        scrolltree.add(self.treeview)
 
        self.hpaned.pack1(scrolltree, resize=False, shrink=True)
        scrolltree.set_size_request(200, -1)
        self.panel = gtk.VBox(False, 0)
        self.panel.show()

        scrollpanel = gtk.ScrolledWindow()
        scrollpanel.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrollpanel.show()
        scrollpanel.add_with_viewport(self.panel)
        scrollpanel.set_size_request(300, -1)

        self.hpaned.pack2(scrollpanel, resize=True, shrink=True)
        #self.hpaned.compute_position(640, 280, 300)
        self.window.show_all()

    def createTreeView(self):
        #TODO create and refresh TreeView
        pass

    def updatePanel(self, widget, item,a):
        """update panel when user select element from treeview"""
        #get data from highlighted selection
        treeselection = self.treeview.get_selection()
        (model, iter) = treeselection.get_selected()
        name_of_data = self.treestore.get_value(iter, 0)
        self.clearPanel()
        numberOfUploaded = 10
        if item[0] == 0:
            if len(item)==1:
                data = self.db.getLastUploaded(numberOfUploaded)
                pass
            elif len(item)==2:
                data=self.db.getImagesByUploadDate(name_of_data)
            elif len(item)==3:
                date = model.get_value(model.get_iter(str(item[0]) +":"+ str(item[1])), 0)
                data=self.db.getImagesByUploadDateAndHosting(date, name_of_data)
                pass
        elif item[0] == 1:
            if len(item) == 1:
                data = self.db.getLastUploaded(numberOfUploaded)
                pass
            elif len(item) == 2:
                data = self.db.getImagesByHostingName(name_of_data)
        else:
            self.clearPanel()
        self.displayData(data)

    
    def displayData(self, elements):
        """display elements on history panel"""
        for element in elements:
            self.addElement(element)
        self.window.show_all()

    def getImageFromHosting(self,data):
        """download image from hosting, create thumb and save to cache folder"""
        urlLink = data[3]
        imgStream = urllib.urlopen(urlLink)
        imgBuffer = imgStream.read()
        imgStream.close()
        #work only for imageshack
        if data[8]=="jpg" or data[8]=="jpeg" or data[8]=="tiff" or data[8]=="tif":
            loader = gtk.gdk.PixbufLoader("jpeg")
        elif data[8]=="bmp":
            loader = gtk.gdk.PixbufLoader("png")
        else:
            loader = gtk.gdk.PixbufLoader(data[8])
        loader.write(imgBuffer)
        loader.close()
        pixbuf = loader.get_pixbuf()
        ratio = float(pixbuf.get_width()) / pixbuf.get_height()
        thumbnailSizeY = thumbnailSizeX = set.getThumbnailSize()
        if ratio > 1:
            thumbnailSizeY /= ratio
        else:
            thumbnailSizeX *= ratio
        pixbuf = pixbuf.scale_simple(int(thumbnailSizeX), int(thumbnailSizeY), gtk.gdk.INTERP_BILINEAR)
        return pixbuf

    def __destroy(self, widget, data=None):
        self.window.destroy()

    def main(self):
        gtk.main()

    def addElement(self, data):
        """add element to history panel with thumb, links and information about image"""
        hbox = gtk.HBox(False, 0)
        self.panel.pack_start(hbox, False, False, 0)
        hbox.show()

        image = self.getImageThumb(data)
        image.set_padding(10,10)
        image.set_tooltip_text(data[6])
        hbox.pack_start(image, False, False, 0)
        image.show()

        vboxSmall = gtk.VBox(True, 0)
        hbox.pack_start(vboxSmall, False, False, 0)
        vboxSmall.show()

        table = gtk.Table(4, 3, False)
        vboxSmall.pack_start(table, True, True, 0)
        table.set_size_request(400, -1)
        table.set_border_width(10)
        table.show()

        labelname = gtk.Label()
        labelname.set_markup("<b>"+_("Original filename:")+"</b>")
        labelname.set_alignment(xalign=0, yalign=0.5)
        labelname.show()
        table.attach(labelname, 0, 1, 0, 1)

        name=gtk.Label(data[6])
        name.set_alignment(xalign=0, yalign=0.5)
        name.show()
        table.attach(name, 1, 2, 0, 1)

        labeldate = gtk.Label()
        labeldate.set_markup("<b>"+_("Upload date:")+"</b>")
        labeldate.set_alignment(xalign=0, yalign=0.5)
        labeldate.show()
        table.attach(labeldate, 0, 1, 1, 2)

        date=gtk.Label(convert_date(data[5]))
        date.set_alignment(xalign=0, yalign=0.5)
        date.show()
        table.attach(date, 1, 2, 1, 2)

        labelsize = gtk.Label()
        labelsize.set_markup("<b>"+_("Filesize:")+"</b>")
        labelsize.set_alignment(xalign=0, yalign=0.5)
        labelsize.show()
        table.attach(labelsize, 0, 1, 2, 3)

        size=gtk.Label(convert_bytes(data[7]))
        size.set_alignment(xalign=0, yalign=0.5)
        size.show()
        table.attach(size, 1, 2, 2, 3)


        labellink=gtk.Label()
        labellink.set_markup("<b>"+_("Links:")+"</b>")
        labellink.set_alignment(xalign=0, yalign=0.5)
        labellink.show()
        table.attach(labellink, 0, 1, 3, 4)

        if isImage(data[9]):
            links, typesOfLinks, basicLinks = createLinks(data[2], data[6], data[4], data[3])
        else:
            links, typesOfLinks, basicLinks = createLinks(data[2], data[6], None, data[3])
        self.links.append(links)
        comboBox = createCombobox(typesOfLinks)
        comboBox.connect("changed", self.copyLink, self.fileNumber)
        #comboBox.show()
	copyButton = gtk.Button(label = "Copy Link")
	copyButton.connect("clicked", self.copyLink, self.fileNumber, 0)
	copyButton.show()        
        self.fileNumber += 1

        table.attach(copyButton, 1, 2, 3, 4)
        #table.attach(comboBox, 1, 2, 3, 4)


        toolButton = gtk.ToolButton(gtk.STOCK_REMOVE)
        toolButton.set_tooltip_text(_("Remove"))
        toolButton.connect("clicked", self.removeElement, self.totalNumberOfElements, data[0])
        table.attach(toolButton, 2,3, 0,3)

        separator = gtk.HSeparator()
        self.panel.pack_start(separator, False, False, 4)
        separator.show()

        self.elements[self.totalNumberOfElements] = hbox
        self.totalNumberOfElements += 1
        self.elements[self.totalNumberOfElements] = separator
        self.totalNumberOfElements += 1

    def removeElement(self, widget, numberOfElement, fileid):
        """remove element from panel and database"""
        data = self.db.getFileById(fileid)
        if isImage(data[9]):
            removeFromCache(data[2])
        self.db.deleteFile(fileid)
        element = self.elements[numberOfElement]
        separator = self.elements[numberOfElement+1]
        self.panel.remove(element)
        self.panel.remove(separator)
        element.destroy()
        separator.destroy()
        del self.elements[numberOfElement]
        del self.elements[numberOfElement+1]

    def copyLink(self, widget, fileNumber, linkType=-1):
        """copy link to clipboard"""
        if linkType < 0:
            linkType = widget.get_active()
        copyToClipBoard(None, self.links[fileNumber][linkType])

    def clearPanel(self):
        """clear panel history by remove all elements"""
        array = self.panel.get_children()
        for i in array:
            self.panel.remove(i)
            i.destroy()
        self.links = []
        self.totalNumberOfElements = 0
        self.elements = {}
        self.fileNumber = 0

    def getImageThumb(self, data):
        if not isImage(data[9]):
            iconsPath = "/usr/share/icons/gnome/32x32/mimetypes/"
            defaultIcon = iconsPath + "empty.png"
            iconName = "gnome-mime-"+data[9].split('/')[0].lower()+"-"+data[9].split('/')[-1].lower()+".png"
            if os.path.exists(iconsPath+iconName):
                pixbuf = gtk.gdk.pixbuf_new_from_file(iconsPath+iconName)
            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file(defaultIcon)
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            return image
        cachePath = getPyShareHomeDirectory() + 'cache/'
        if not os.path.exists(cachePath):
            os.makedirs(cachePath)
        #filename = cachePath + md5(data[6].join(data[5])).hexdigest()
        #if os.path.exists(filename):
        pixbuf = getThumbnailFromCache(data[2])
        if pixbuf :
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            return image
        else:
            pixbuf = self.getImageFromHosting(data)
            filename=cachePath + md5(data[2]).hexdigest()
            image = gtk.Image()
            image.set_from_pixbuf(pixbuf)
            if(data[8]=="jpg" or data[8]=="gif"):
                pixbuf.save(filename, "jpeg")
            else:
                pixbuf.save(filename, data[8])
            return image

if __name__ == "__main__":
    hw = History_GTK()
    hw.main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2009>  <Sebastian Kacprzak> <naicik |at| gmail |dot| com>

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


def importErrorDialog(txt):
    """shows basic error dialog with given text and than calls sys.exit
    tries to show message using Tkinter, fallbacks to  zenity fallback to xterm"""
    
    from os import system
    zenityInstalled = system("command -v zenity") == 0
    if zenityInstalled:
        system("zenity --info --text='" + str(txt) + "'")
    else:
        try: # try to show tkinker dialog
            import Tkinter
            master = Tkinter.Tk()
            w = Tkinter.Message(master, text=txt)
            w.pack()
            Tkinter.mainloop()
        except ImportError:
            system("xterm -hold -geometry 150x1 -bg red -T '" + str(txt) + "' -e true")
    from sys import exit
    exit()

#change working directory to PyShare_GTK path. This is needed as long as paths are relative.
import os
try:
    from sys import path as PySharePath
    from os import chdir
    chdir(PySharePath[0])
    import gettext
    gettext.install('PyShare_GTK', 'translations')
except ImportError:
    print _("can't change working dir. Translations and icons may not work") # not fatal

#import all needed libralies. Failure is fatal
try:
    import pygtk
    pygtk.require('2.0') # comboboxes needs pygtk 2.4 or higher, however they work fine with package 2.14.1-1ubuntu1 - probably version number differs..
    import gtk
except ImportError:
    importErrorDialog(_("This script needs gtk and pygtk 2.0 or higher"))
except AssertionError:
    importErrorDialog(_("This script needs pygtk 2.0 or higher"))
try:
    from threading import Lock, BoundedSemaphore
    from gobject import GError
    from urllib import url2pathname
    from pluginWrapper import uploadFile as uploadFileWrapper, runMethodInThread
    from History_GTK import History_GTK
    from Settings_GTK import Settings_GTK
    from Settings import Settings
    set = Settings()
    from DB import DB
    db=DB()
    from helpers.gtkHelper import createCombobox, copyToClipBoard, populateCombobox, createThumbnail, getMimeTypes, saveThumbnail, isImage
    from plugins import getUploader
    #if allowOneInstanceOnly:
    if set.getAllowOneInstanceOnly():
        from AllowOnlyOneInstance import instanceExists, sendFilesToInstance
except ImportError, error:
    importErrorDialog(error)

def showDialog(parent, description, title='PyShare dialog'):
    """shows gtk dialog with given title and description"""
    parent.dialog = gtk.MessageDialog(
                                       parent=None,
                                       flags=gtk.DIALOG_DESTROY_WITH_PARENT,
                                       type=gtk.MESSAGE_INFO,
                                       buttons=gtk.BUTTONS_CLOSE,
                                       message_format=description
                                       )
    parent.dialog.set_title(title)
    parent.dialog.run()
    parent.dialog.destroy()

class MainWindow:
    __pbars = []
    __comboBoxes = []
    links = []
    __uploadsCompleted = 0 # uploads that ended - failed uploads also counts
    __uploadsErrors = 0 # failed uploads
    __uploadsCompletedLock = Lock()
    #__uploaders = []
    __commonLinkNames = None
    __semaphore = BoundedSemaphore(set.getMaxConnections())
    __menuFiles = []
    __menuItemAll = None
  
    def __destroy(self, widget, data=None):
        """Called before quiting"""
        gtk.main_quit()
        import sys 
        sys.exit() # kill all background threads like unfinished uploads

    def __windowClicked(self, widget=None, data=None):
        self.__statusIcon.set_blinking(False)

    def __fileUploadEnded(self, fileNumber, errorOccured, imageLinks=None,file=""):
        """if upload was successfull than attaches imageLinks to combobox with given fileNumber and shows it
        otherwise it sets proggressbar message to indicate upload failure
        imageLinks and file are ignored if errorOccured is True"""
        if not errorOccured:
            self.links[fileNumber] = imageLinks[0] # there is one thread per file so this should be thread safe
            db.addFile(getUploader(file).NAME, imageLinks[2][0], imageLinks[2][1], imageLinks[2][2], os.path.basename(file), os.path.getsize(file),file.split('.')[-1].lower(), getMimeTypes(file))
            if isImage(getMimeTypes(file)):
                saveThumbnail(createThumbnail(file), file, imageLinks[2][0])
        self.__uploadsCompletedLock.acquire()
        try: #rather not needed
            self.__uploadsCompleted += 1
            if errorOccured:
                self.__uploadsErrors += 1
        finally:
            self.__uploadsCompletedLock.release()
        try:
            gtk.gdk.threads_enter()
            if errorOccured:
                self.__pbars[fileNumber].set_text(_("upload failed"))
            else:
                self.__pbars[fileNumber].set_text(_("upload completed"))
                combobox = self.__comboBoxes[fileNumber]
                linkTypes = imageLinks[1]
                populateCombobox(combobox, linkTypes)
                combobox.show()
                self.__populateStatusIconMenuForFile(fileNumber, linkTypes)
                if self.__uploadsCompleted > 1:
                    self.__createCopyAllLinks()
                    self.setWindowSize()
            self.__statusIcon.set_tooltip(_("Uploaded ") + str(self.__uploadsCompleted) + _(" of ") + str(len(self.__comboBoxes)) + _(" files."))
            if(self.__uploadsCompleted == len(self.__comboBoxes)):
                if (set.getBlinkIcon()):
                    self.__statusIcon.set_blinking(True)
                if set.getShowNotifications():
                    try:
                        import pynotify
                        if pynotify.init("PyShare"):
                            notification = None
                            if self.__uploadsErrors == 0:
                                notification = pynotify.Notification(_("File(s) uploaded successfully"), _("Click the preferred link textbox to copy the file url(s) to your clipboard."), "go-up")
                            elif self.__uploadsErrors < self.__uploadsCompleted :
                                notification = pynotify.Notification(_("Some upload(s) failed"), _("For successfully upload(s), click the preferred link textbox to copy the file url(s) to your clipboard. Please try failed upload(s) again."), "go-up")
                            else:
                                notification = pynotify.Notification(_("Upload(s) Failed"), _("Please verify your internet connection and that the file(s) have appropriate permissions then try again."), "go-up")
                            notification.show()
                    except ImportError: pass
        finally:
            gtk.gdk.threads_leave()

    def fileUploaded(self, imageLinks, fileNumber, file=""):
        """attaches imageLinks to buttons with given fileNumber"""
        self.__fileUploadEnded(fileNumber, False, imageLinks, file)

    def fileUploadFailed(self,fileNumber):
        """sets proggressbar message to indicate upload failure"""
        self.__fileUploadEnded(fileNumber, True)

    def copyAllLinks(self, widget, linkType=-1):
        """copies all links with selected widget type to clipboard"""
        if linkType < 0: # 0 also give false
            linkType = widget.get_active() # get selected combo box item
        allLinks = ''
        for link in self.links:
            if link:
                allLinks += link[linkType]  + "\n" # to lazy for .join ;p
        copyToClipBoard(None, allLinks)

    def copyLink(self, widget, fileNumber, linkType=-1):
        """copies link with given fileNumber to clipboard. 
        If linkType is negative type is fetched from widget"""
        #copyToClipBoard(None, self.links[fileNumber][widget.get_active()])
        if linkType < 0: # 0 also give false
            linkType = widget.get_active() #get selected combo box item
        copyToClipBoard(None, self.links[fileNumber][linkType])
        self.__pbars[fileNumber].set_text(_("copied to clipboard")) #somehow don't want to work with gtk lock, but works without it, no thread read from __pbars so that shouldn't be important
        self.__pbars[fileNumber].modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse("#6495ed"))

    def __statusIconClicked(self, icon):
        """hides or shows window to notification area, and turns off icon blinking"""
        if not self.window.is_active():
            self.window.present()
        else:
            self.window.hide()
        self.__statusIcon.set_blinking(False)

    def insertFilesToStatusIconMenu(self, correctFiles, insertPosition):
        """creates entries for given correctFiles in given insertPosition"""
        for file in correctFiles:
            sm = gtk.Menu()
            menuItem = gtk.MenuItem(file.split('/')[-1])
            menuItem.set_submenu(sm)
            self.menu.insert(menuItem, insertPosition)
            self.__menuFiles.insert(insertPosition,sm)
            insertPosition += 1


    def __populateStatusIconMenuForFile(self,fileNumber,linkTypes):
        sm = self.__menuFiles[fileNumber]
        linkNumber = 0
        for name in linkTypes:
            menuItem = gtk.MenuItem(name)
            menuItem.connect("activate", self.copyLink, fileNumber, linkNumber)
            sm.append(menuItem)
            linkNumber += 1
        self.__populateMenuItemAll(linkTypes)

    def __populateMenuItemAll(self, linkTypes):
        """creaties submenu with link types that exist in all uploaded files
        clicking on given entry copies links to clipboard"""
        sm = gtk.Menu()
        if not self.__menuItemAll:
            self.menu.append(gtk.MenuItem()) #separator
            self.__menuItemAll = gtk.MenuItem(_('All'))
            self.menu.append(self.__menuItemAll)
        self.__menuItemAll.set_submenu(sm)
        
        linkNumber = 0
        linkNames = self.getCommonLinkNames(linkTypes)
        for name in linkNames:
            menuItem = gtk.MenuItem(name)
            menuItem.connect("activate", self.copyAllLinks, linkNumber)
            sm.append(menuItem)
            linkNumber += 1

    def __createStatusIcon(self):
        """creates self.__statusIcon and loads it icon if possible"""
        self.__statusIcon = gtk.StatusIcon()
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file("icon.png")
            self.window.set_icon(pixbuf) # windows icon is shown in gnome panel or during windows switch
            if set.getShowIcon():
                self.__statusIcon.set_tooltip(_("Uploading ") + str(len(self.__comboBoxes)) + _(" files."))
                self.__statusIcon.set_from_pixbuf(pixbuf)
                self.__statusIcon.connect('activate', self.__statusIconClicked)
                self.__statusIcon.set_visible(True)

        except GError, exc:
            print _("can't load icon"), exc # non fatal, we lose only tray icon

    def __createStatusIconMenu(self, correctFiles):
        """creates status icon menu containg 'close' and entries for given correctFiles"""
        self.menu = gtk.Menu()
        
        self.insertFilesToStatusIconMenu(correctFiles, 0)
        #if len(correctFiles) > 1:
        
        #self.__populateMenuItemAll()

        self.menu.append(gtk.MenuItem()) #separator
        menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        menuItem.connect('activate', self.__destroy, self.__statusIcon)
        self.menu.append(menuItem)

        self.__statusIcon.connect('popup-menu', self.__statusIconMenu, self.menu)

    def __statusIconMenu(self, widget, button, time, menu=None):
        """popups the status icon menu"""
        self.__statusIcon.set_blinking(False)
        if button == 3:
            if menu:
                menu.show_all()
                menu.popup(None, None, gtk.status_icon_position_menu, button, time, self.__statusIcon)

    def __toolButtonSettingsClicked(self, toolButton=None):
        """creates settings dialog"""
        Settings_GTK(self.window)

    def __toolButtonHistoryClicked(self, toolButton=None):
        """creates history window"""
        History_GTK(self.window)

    def __toolButtonScreenshotClicked(self, toolButton=None):
        """takes screenshots and sends it"""
        from sendScreenshot import getScreenshot
        try:
            #TODO: ask about screenshot type
            #TODO: use plugin wrapper to run in diffrent thread
            screenshotPath = getScreenshot(True)
            self.addFiles([screenshotPath,])
        except Exception, e:
            showDialog(self, str(e), "getting screenshot failed")
        

    def __createToolButton(self, pixbuf, text, tooltipText, clickedAction):
        """returns gtk.ToolButton with given atributes"""
        
        image = gtk.Image()
        image.set_from_pixbuf(pixbuf)
        toolButton = gtk.ToolButton(image, text)
        toolButton.connect("clicked", clickedAction)
        toolButton.set_tooltip_text(tooltipText)
        return toolButton


    def __createToolbar(self):
        """returns gtk.Toolbar() with Screenshot,History and Configure buttons"""
        toolbar = gtk.Toolbar()
        toolbar.set_style(gtk.TOOLBAR_ICONS)
        
        icon_theme = gtk.icon_theme_get_default()
        iconSize = 32

        try:
            pixbuf = icon_theme.load_icon("media-record", iconSize, 0)
        except:
            pixbuf = None # it seams that some icon sets don't have some set icons
        toolbar.insert(self.__createToolButton(pixbuf, _("Screenshot"), _("Take a desktop, window, or area screenshot"), self.__toolButtonScreenshotClicked), 0)

        try:
            pixbuf = icon_theme.load_icon("clock", iconSize, 0)#stock_book_blue#emblem-documents
        except:
            pixbuf = None
        toolbar.insert(self.__createToolButton(pixbuf, _("History"), _("View previous uploads"), self.__toolButtonHistoryClicked), 1)

        try:
            pixbuf = icon_theme.load_icon("preferences-system", iconSize, 0)
        except:
            pixbuf = None
        toolbar.insert(self.__createToolButton(pixbuf, _("Configure"), _("PyShare settings"), self.__toolButtonSettingsClicked), 2)

        toolbar.set_style(gtk.TOOLBAR_BOTH)
        toolbar.set_show_arrow(False)
        toolbar.show_all()
        return toolbar




    def addFiles(self, urls, firstAdding=False):
        """adds progressbar, buttons, thumbnail and status menu entry for each file to GUI.
        calls set windows size
        if there is more than one file in the windows also shows copy all link combobox
        starts uploding given files"""
        files = self.urlsToPaths(urls)
        addedFiles = []
        vbox = self.vboxFiles
        numberOfFilesAddedEarierl = len(self.__comboBoxes)
        totalNumberOfFiles = numberOfFilesAddedEarierl
        for file in files:
            hbox = gtk.HBox(False, 0)
            vbox.pack_start(hbox, False, False, 0)
            hbox.show()

            #thumbnail
            image = gtk.Image()
            image.set_from_pixbuf(createThumbnail(file))
            hbox.pack_start(image, False, False, 8)
            image.show()

            vboxSmall = gtk.VBox(False, 5)
            hbox.pack_start(vboxSmall, False, False, 0)
            vboxSmall.show()
            
            #filename
            label = gtk.Label(file.split('/')[-1])
            label.set_alignment(0, 0.5)
            vboxSmall.pack_start(label, False, False, 0)
            label.show()
            
            #progress bar
            pbar = gtk.ProgressBar()
            self.__pbars.append(pbar)
            vboxSmall.pack_start(pbar, False, False, 0)
            pbar.show()

            #comboBox = createCombobox(uploader.getReturnedLinkTypes())
            comboBox = createCombobox()
            self.links.append([])
            comboBox.connect("changed", self.copyLink, totalNumberOfFiles)
            comboBox.connect("notify::popup-shown", self.__windowClicked)
            comboBox.show() # "show" comboboxes to make windows size calculation precise(comboboxes will be hidden again before window will be desplayed)
            self.__comboBoxes.append(comboBox)

            vboxSmall.pack_start(comboBox, False, False, 0)

            

            separator = gtk.HSeparator()
            vbox.pack_start(separator, False, False, 4)
            separator.show()

            uploader = getUploader(file)
            addedFiles.append(file)
            uploadFileWrapper(uploader,self.fileUploadFailed,
                file,self.fileUploaded,self.progress,totalNumberOfFiles, self.__semaphore)
            totalNumberOfFiles += 1
            
        if firstAdding:
            self.__addFooter()
            self.__createStatusIconMenu(addedFiles)
        else:
            self.insertFilesToStatusIconMenu(addedFiles, numberOfFilesAddedEarierl)
            
#        if totalNumberOfFiles > 1:
#            self.__createCopyAllLinks()

        self.setWindowSize()

        while numberOfFilesAddedEarierl < totalNumberOfFiles: # hide comboboxes, they will be displayed when links are ready
            self.__comboBoxes[numberOfFilesAddedEarierl].hide()
            numberOfFilesAddedEarierl += 1
        self.__statusIcon.set_blinking(False)

    def __createCopyAllLinks(self):
        if self.__copyAllLinksCombobox:
            self.__copyAllLinksCombobox.destroy()
        else:
            label = gtk.Label(_("All files:"))
            self.vboxCopyAllLinks.pack_start(label, False, False, 0)
            label.show()
        comboBox = createCombobox(self.__commonLinkNames)
        comboBox.connect("changed", self.copyAllLinks)
        comboBox.connect("notify::popup-shown", self.__windowClicked)
        self.vboxCopyAllLinks.pack_start(comboBox, False, False, 0)
        comboBox.show()
        self.__copyAllLinksCombobox = comboBox
        self.vboxCopyAllLinks.show()

    def __addFooter(self):
        align = gtk.Alignment(0.5, 0.5, 0, 0)
        self.vboxMain.pack_start(align, False, False, 0)
        align.show()

        hbox = gtk.HBox(False, 5)
        hbox.set_border_width(10)
        align.add(hbox)
        hbox.show()

        self.vboxCopyAllLinks = gtk.VBox(False, 0)
        hbox.pack_start(self.vboxCopyAllLinks, False, False, 0)
        self.__copyAllLinksCombobox = None

# Commented out Close button
#        button = gtk.Button(_("close"))
#        button.connect("clicked", self.__destroy)
#        hbox.pack_start(button, False, False, 2)
#        button.show()


    def setWindowSize(self):
        vboxMainSize = self.vboxMain.size_request()
        windowSize = self.window.size_request()
        width = windowSize[0]
        if width < vboxMainSize[0]:
            width = vboxMainSize[0]
        heigh = vboxMainSize[1] + 8 # error margin;)
        if set.getMaximumHeight() < heigh:
            heigh = set.getMaximumHeight()

        self.window.set_size_request(int(width) + 4, int(heigh))

    def progress(self, fileNumber, download_t=0, download_d=0, upload_t=0.5, upload_d=1):
	"""Callback function invoked when download/upload has progress.
        sets fraction and text on progresbar with given fileNumber"""
        if upload_t != 0:
            prog = upload_d / upload_t
            try: # rather not needed
                gtk.gdk.threads_enter()
                self.__pbars[fileNumber].set_fraction(prog)
                if prog < 1:
                    self.__pbars[fileNumber].set_text(str(upload_d) + " / " + str(upload_t))
                else:
                    self.__pbars[fileNumber].set_text(_("Please wait"))
            finally:
                gtk.gdk.threads_leave()


    def urlsToPaths(self,urls):
        """removes garbage from input"""
        if not urls:
            return []
        cutFirstNSigns=0
        if not isinstance(urls,list):
            urls = urls.split('\r\n')

        if urls[0].startswith('file://'): # nautilus, rox
            cutFirstNSigns = 7 # 7 is len('file://')
 	elif urls[0].startswith('file:\\\\\\'): # windows backslash madness;)
            cutFirstNSigns = 8 # 8 is len('file:///')
 	elif urls[0].startswith('file:'): # xffm
            cutFirstNSigns = 5 # 5 is len('file:')
        
        paths = []
        for url in urls:
            path = url[cutFirstNSigns:]
            path = url2pathname(path) # escape special chars
            if path:
                paths.append(path)
        return paths

    def dropAction(self, widget, context, x, y, selection, target_type, timestamp):
        """called when something is dropped on window. tries to upload it"""
	self.addFiles(selection.data.strip('\x00'))

    def getCommonLinkNames(self, linkNames):
        """gets intersections of returned link types of uploaders"""
        if not self.__commonLinkNames:
            self.__commonLinkNames = linkNames
            return linkNames
        self.__commonLinkNames = filter(lambda x:x in self.__commonLinkNames, linkNames)
        return self.__commonLinkNames
        #checkedUploaders = [self.__uploaders[0]]
        #commonLinkNames = set (self.__uploaders[0].getReturnedLinkTypes())
        #commonLinkNames = self.__uploaders[0].getReturnedLinkTypes()
#        i = 0
#        commonLinkNames = self.menu.get(0)
#        for uploader in self.__uploaders:
#            if uploader not in checkedUploaders:
#                checkedUploaders.append(uploader)
#                #commonLinkNames = commonLinkNames.intersection(set(uploader.getReturnedLinkTypes())) # not stable, elements move on lists
#                commonLinkNames = filter(lambda x:x in commonLinkNames, uploader.getReturnedLinkTypes())
#        return commonLinkNames

    def __init__(self, files):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_resizable(True)
        self.window.connect("destroy", self.__destroy)
        self.window.set_title("PyShare 0.6.2 - SENG310")
        self.window.set_border_width(0)
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.window.add(scroll)
        scroll.show()
        align = gtk.Alignment(0.5, 0.0, 0, 0)
        scroll.add_with_viewport(align)
        align.show()
        
        self.vboxMain = gtk.VBox(False, 0)
        align.add(self.vboxMain)
        self.vboxMain.show()
        toolbar = self.__createToolbar()
        self.vboxMain.pack_start(toolbar, False, False, 0)
        toolbar.show()

        label = gtk.Label("Drop files here to start upload")
        label.set_size_request(50, 50)
        label.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("white")) 
        eb = gtk.EventBox()
        eb.add(label)
        eb.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("grey"))
        self.vboxMain.pack_start(eb, False, False, 20)
        label.show()
        eb.show()

        self.vboxFiles = gtk.VBox(False, 0)
        self.vboxMain.pack_start(self.vboxFiles, False, False, 0)
        self.vboxFiles.show()

        self.__createStatusIcon()
        self.addFiles(files, True)

        #add drop handling
        self.window.drag_dest_set(0, [], 0)
        self.window.connect('drag_data_received', self.dropAction)
        dnd_list = [ ( 'text/uri-list', 0, 80 ) ]
        self.window.drag_dest_set( gtk.DEST_DEFAULT_MOTION |
                  gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                  dnd_list, gtk.gdk.ACTION_COPY)
        #add click handling
        self.window.add_events(gtk.gdk.BUTTON_PRESS_MASK)
        self.window.connect("button-press-event", self.__windowClicked)

        self.window.show()

        

mw = None # instance of the main window

def addLinksToInstance(files):
    if(files):
        assert(mw)
        mw.addFiles(files)
        

def uploadFilesGUI(files):
    """sends files given by paths, separated by new lines"""
    if set.getAllowOneInstanceOnly():
        if instanceExists(addLinksToInstance):
            sendFilesToInstance(files)
            return
    gtk.gdk.threads_init()
    global mw
    gtk.gdk.threads_enter()
    mw = MainWindow(files)
    gtk.gdk.threads_leave()
    gtk.main()

if __name__ == "__main__":
    from sys import argv
    args = argv[1:]
    uploadFilesGUI(args)



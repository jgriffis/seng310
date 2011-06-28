#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2009-2011>  <Sebastian Kacprzak> <naicik |at| gmail |dot| com>

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

import pygtk
pygtk.require("2.0")
import gtk.glade
from helpers.gtkHelper import createCombobox
from Settings import Settings
from plugins import UNIVERSAL_HANDLERS, FILETYPE_HANDLERS, PLUGINS_WITH_PASSWORDS

__author__ = "Sebastian Kacprzak <naicik at gmail.com>"
__date__ = "$2009-12-12 14:22:55$"

import gettext
translationsDomainName = 'settings' #glade and python file use same domain name, because for user it is the same window
translationsDirName = 'translations'
try:
    translation = gettext.translation(translationsDomainName,translationsDirName)
    _ = translation.gettext
except IOError:
    def return_english(text):
        return text
    _ = return_english
    print "translations for your language don't yet exist"

class Settings_GTK():

    def __init__(self, caller=None):
        self._settings_class = Settings()
        self._settings_dict = self._settings_class.getSettings()

        self.__parent = caller

        gtk.glade.bindtextdomain(translationsDomainName, translationsDirName)
        gtk.glade.textdomain(translationsDomainName)

        gladefile = "settings.glade"
        self.__wTree = gtk.glade.XML(gladefile)

        self.__window = self.__wTree.get_widget("Settings")
        self.__optipngBox = self.__wTree.get_widget("hboxOptipng")
        self.__comboboxFileType = self.__wTree.get_widget("comboboxFileType")
        self.__hscaleCompression = self.__wTree.get_widget("hscaleCompression")
        self.__labelScaleMax = self.__wTree.get_widget("labelScaleMax")

        self.__window.connect("destroy", self._destroy)

        dic = {
            "on_buttonOK_clicked": self.__buttonOKClicked,
            "on_buttonReset_clicked": self.__buttonResetClicked,
            "on_hscaleCompression_value_changed": self.__scaleCompressionValueChanged,
            "on_comboboxFileType_changed": self.__comboboxFileTypeChanged,
            "on_buttonInstallOptipng_clicked": self.__buttonInstallOptipng,
            "on_buttonGetCurrentHeight_clicked": self.__buttonGetCurrentHeightClicked,
            "on_spinbuttonNumberOfConnections_value_changed":self.__spinbuttonNumberOfConnections_value_changed,
            "on_comboboxClipboard_changed":self.__comboboxClipboard_changed,
            "on_checkbuttonOneInstance_toggled":self.__checkbuttonOneInstance_toggled,
            "on_spinbuttonHeight_value_changed":self.__spinbuttonHeight_value_changed,
            "on_spinbuttonThumb_value_changed":self.__spinbuttonThumb_value_changed,
            "on_checkbuttonNotification_toggled":self.__checkbuttonNotification_toggled,
            "on_checkbuttonIcon_toggled":self.__checkbuttonIcon_toggled,
            "on_checkbuttonBlink_toggled":self.__checkbuttonBlink_toggled,
            "on_checkbuttonUseProxy_toggled":self.__on_checkbuttonUseProxy_toggled,
            "on_entryProxyAddress_changed":self.__on_entryProxyAddress_changed,
            "on_entryProxyPort_changed":self.__on_entryProxyPort_changed,
#            "on_entryProxyUserName_changed":self.__on_entryProxyUserName_changed,
#            "on_entryProxyPassword_changed":self.__on_entryProxyPassword_changed,
            "on_comboboxProxyAuthentication_changed":self.__on_comboboxProxyAuthentication_changed
        }
        self.__wTree.signal_autoconnect(dic)

        self.__checkInstalledComponents()
        self.__initUploaderTabs()
        self.__loadSettings()

        self.__window.show()
        #hide not yet implemented elements
        self.__wTree.get_widget("buttonInstallOptipng").hide()
#        self.__wTree.get_widget("label17").hide()


    def _destroy(self, widget=None):
        """save changes to db"""
        set = self._settings_class
        _save_uploader_credentials(self.__accounts.items(), set)
        set.setProxyCrednetials(self.__wTree.get_widget("entryProxyUserName").get_text(), self.__wTree.get_widget("entryProxyPassword").get_text())
        set.saveSettingsToDB()
        

    def __checkInstalledComponents(self):
        from os import system
        self.__optipngInstalled = system("command -v optipng") == 0

    def __initUploaderTabs(self):
        self.__createUploadersTab()
        self.__createAccountsTab()


    def __loadSettings(self):
        self.__comboboxFileType.set_active(0)
        if not self.__optipngInstalled:
            self.__optipngBox.show()
        self.__setComponentsToValues(self._settings_dict)

    def __setComponentsToValues(self, settings):
        """set widget to values from given settings"""
        self.__wTree.get_widget("checkbuttonOneInstance").set_active(settings["allowOneInstanceOnly"])
        self.__wTree.get_widget("spinbuttonHeight").set_value(settings["maximumHeight"])
        self.__wTree.get_widget("spinbuttonThumb").set_value(settings["thumbnailSize"])
        self.__wTree.get_widget("checkbuttonNotification").set_active(settings["showNotifications"])
        self.__wTree.get_widget("checkbuttonIcon").set_active(settings["showIcon"])
        self.__wTree.get_widget("checkbuttonBlink").set_active(settings["blinkIcon"])

        self.__wTree.get_widget("spinbuttonNumberOfConnections").set_value(settings["maxConnections"])
        self.__wTree.get_widget("checkbuttonUseProxy").set_active(False) # needed for Reset calls only, may be later overwritten by setCredentials call
        self.__wTree.get_widget("entryProxyAddress").set_text(settings["proxyName"])
        self.__wTree.get_widget("entryProxyPort").set_text(str(settings["proxyPort"]))
        self.__setCredentialsForUploaders()
        self.__setCredentialsForProxy()
        self.__wTree.get_widget("comboboxProxyAuthentication").set_active(settings["proxyAuthenticationType"])

        clipboardTypeIndeks = self.convertClipoardTypeToIndeks(settings["clipboardType"])
        self.__wTree.get_widget("comboboxClipboard").set_active(clipboardTypeIndeks)

        fileTypeIndeks = self.convertFileTypeToIndex(settings["fileType"])
        self.__wTree.get_widget("comboboxFileType").set_active(fileTypeIndeks)
        self.__wTree.get_widget("hscaleCompression").set_value(settings["fileSize"])

    def convertClipoardTypeToIndeks(self, type):
        """helper method for preferred clipboard type combobox
        returns string that is displayed under given index

        """
        clipboardTypeIndeks = 1
        if type == "PRIMARY":
            clipboardTypeIndeks = 0
        return clipboardTypeIndeks

    def convertClipoardIndexToType(self, index):
        """helper method for preferred clipboard type combobox
        returns string that is displayed under given index
        do note that this method may be replaced by gtk.ComboBox.get_active_text from PyGTK >= 2.6
        """
        if index == 0:
            return "PRIMARY"
        else:
            return "CLIPBOARD"

    def convertFileTypeToIndex(self, type):
        """helper method for preferred screenshot type combobox
        returns index of given filetype
        """
        fileTypeIndeks = 0
        if type == "jpg":
            fileTypeIndeks = 1
        elif type == "tiff":
            fileTypeIndeks = 2
        elif type == "bmp":
            fileTypeIndeks = 3
        return fileTypeIndeks

    def convertFileIndexToType(self, index):
        """helper method for preferred screenshot type combobox
        returns string that is displayed under given index
        do note that this method may be replaced by gtk.ComboBox.get_active_text from PyGTK >= 2.6
        """
#        if index == 0:
#            return "png"
        if index == 1:
            return "jpg"
        if index == 2:
            return "tiff"
        if index == 3:
            return "bmp"
        return "png" #png is default return it if no index is selected(fe:-1)


    def __createUploadersTab(self):
        """inserts entries for each file type that have assignet uploader"""
        vbox = self.__wTree.get_widget("vboxUploaders")
        
        uploadersDic = FILETYPE_HANDLERS
        defaultUploaders = UNIVERSAL_HANDLERS

        #sort uploaders by file type
        fileTypes = uploadersDic.keys()
        fileTypes.sort()

        #put non default uploaders to vbox
        for fileType in fileTypes:
            hbox = self.__createUploderHBox(fileType, uploadersDic[fileType])
            vbox.pack_start(hbox, False, False, 8)

        #put default uploader to vbox
        hbox = self.__createUploderHBox(_("Default"), defaultUploaders, "*")
        vbox.pack_start(hbox, False, False, 8)

        vbox.show_all()

        
    def __createUploderHBox(self, labelName, uploaders, fileType=None):
        """returns HBox with label with file type, and combobox with given uploaders. 
        All given uploaders should be capable of handling given fileType"""
        if not fileType:
            fileType = labelName
        hbox = gtk.HBox(True, 0)
        label = gtk.Label(labelName)
        hbox.pack_start(label, False, True, 0)
        combobox =  createCombobox(uploaders)
        hbox.pack_start(combobox, False, True, 0)
        self.__initUploaderComboboxSelectedValue(fileType, uploaders, combobox)
        combobox.connect("changed", self.__comboboxPrefferedUploader_changed, labelName, uploaders)
        return hbox

    def __createAccountsTab(self):
        table = self.__wTree.get_widget("tableAccounts")
        #store refrences to generated fields, to allow easy acces to them latter
        #key is plugin name, value is list containg usernameEntry, 
        #passwordEntry and in use checkbutton (in that order)
        self.__accounts = {}
        #first row is header
        table.resize(len(PLUGINS_WITH_PASSWORDS)+1,4)
        row = 1
        for plugin in PLUGINS_WITH_PASSWORDS:
            nameLabel = gtk.Label(plugin.NAME)
            table.attach(nameLabel, 0, 1, row, row+1)
            nameLabel.show()

            usernameEntry = gtk.Entry()
            table.attach(usernameEntry, 1, 2, row, row+1)
            usernameEntry.show()

            passwordEntry = gtk.Entry()
            passwordEntry.set_visibility(False)
            table.attach(passwordEntry, 2, 3, row, row+1)
            passwordEntry.show()

            checkbutton = gtk.CheckButton()
            checkbutton.connect("toggled", self._uploaderCheckbuttonToggled, plugin.NAME)
            table.attach(checkbutton, 3, 4, row, row+1)
            # if password is required do not allow user to uncheck it
            checkbutton.set_sensitive(not plugin.PASSWORD_REQUIRED)
            checkbutton.show()

            account = [usernameEntry, passwordEntry, checkbutton]
            self.__accounts[plugin.NAME] = account
            row += 1

    def _uploaderCheckbuttonToggled(self, widget, pluginName):
        areCredentialsUsedSettingName = self._settings_class.getSettingNameForUsingUploaderPassword(pluginName)
        self._settings_dict[areCredentialsUsedSettingName] = widget.get_active()

    def __initUploaderComboboxSelectedValue(self, fileType, uploaders, combobox):
        if not uploaders:
            return # nothing to select from(combobox is empty)
        selectedUploader = self._settings_dict["preferredUploaders"][fileType]
        if selectedUploader in uploaders:
            selectedUploaderIndex = uploaders.index(selectedUploader)
        else:
            #uploader have not been found: try to select default one
            selectedUploaderIndex = 0
            self._settings_dict["preferredUploaders"][fileType] = uploaders[selectedUploaderIndex]
        combobox.set_active(selectedUploaderIndex)
        
    def __setCredentialsToWidgets(self, areCredentialsUsedSettingName, checkbuttonCredentialsUsedWidget,
        credentialsName, nameWidget, passWidget, checkbutton_sensitive = True):
        """areCredentialsUsedSettingName - setting name with value indicating if this credentials are used
        checkbuttonCredentialsUsedWidgetName - checkbutton that should show if credentials are used
        getCredentialsFunction - function that will return credentials
        nameWidgetName - widget that should be populated with credential name
        passWidgetName - widget that should be populated with credential password
        """

        credentials = self._settings_class.getCredentials(credentialsName)
        if credentials:
            user, password = credentials
            nameWidget.set_text(user)
            passWidget.set_text(password)
            del user
            del password
        else:
            nameWidget.set_text("")
            passWidget.set_text("")
        checkbuttonCredentialsUsedWidget.set_active(self._settings_dict[areCredentialsUsedSettingName])

    def __setCredentialsForProxy(self):
        """loads stored proxy credentials"""
        self.__setCredentialsToWidgets("useProxy",
            self.__wTree.get_widget("checkbuttonUseProxy"),
            "proxy",
            self.__wTree.get_widget("entryProxyUserName"),
            self.__wTree.get_widget("entryProxyPassword"))

    def __setCredentialsForUploaders(self):
        """loads stored accounts credentials"""
        for name, accountWidgets in self.__accounts.items():
            self.__setCredentialsToWidgets(
                self._settings_class.getSettingNameForUsingUploaderPassword(name),
                accountWidgets[2],
                name,
                accountWidgets[0],
                accountWidgets[1]
            )

    def __buttonOKClicked(self, widget):
        self.__window.destroy()


    def __buttonResetClicked(self, widget):
        self.__setComponentsToValues(self._settings_class.getDefaultSettings())
        #self.__optipngBox.show()
        
    def __scaleCompressionValueChanged(self, widget):
        val = widget.get_value()
        if (not self.__optipngInstalled) and val == 0 and self.__comboboxFileType.get_active() == 0:
            self.__hscaleCompression.set_value(1)
        

    def __comboboxFileTypeChanged(self, widget):
        #if change from png to jpg change hscaleValue, change labels
        index = self.__comboboxFileType.get_active()
        if  index != 0: # not png
            self.__optipngBox.hide()
        if index != 1: # not jpg
            self.__labelScaleMax.set_text(_("shorter\ntime"))
            self.__hscaleCompression.set_value(0)
            if not self.__optipngInstalled and self.__comboboxFileType.get_active() == 0: # png
                self.__optipngBox.show()
                self.__hscaleCompression.set_value(1)
        else:
            self.__labelScaleMax.set_text(_("better\nquality"))
            self.__hscaleCompression.set_value(75)

        value = self.convertFileIndexToType(index)
        self._settings_dict["fileType"] = value
        self._settings_dict["fileSize"] = self.__hscaleCompression.get_value()

        
    def __buttonInstallOptipng(self, widget):
        print "install optipng"
        #if system("command -v apt-get") == 0:
        self.__optipngBox.hide()

    def __buttonGetCurrentHeightClicked(self, widget):
        if self.__parent:
            parentSize = self.__parent.get_size()
            height = parentSize[1]
            spingButtonHeight = self.__wTree.get_widget("spinbuttonHeight")
            spingButtonHeight.set_value(height)

    def __spinbuttonNumberOfConnections_value_changed(self, widget):
        self._settings_dict["maxConnections"] = widget.get_value()

    def __comboboxClipboard_changed(self, widget):
        index = widget.get_active()
        value = self.convertClipoardIndexToType(index)
        self._settings_dict["clipboardType"] = value

    def __checkbuttonOneInstance_toggled(self, widget):
        self._settings_dict["allowOneInstanceOnly"] = widget.get_active()

    def __spinbuttonHeight_value_changed(self, widget):
        self._settings_dict["maximumHeight"] = widget.get_value()

    def __spinbuttonThumb_value_changed(self, widget):
        self._settings_dict["thumbnailSize"] = widget.get_value()

    def __checkbuttonNotification_toggled(self, widget):
        self._settings_dict["showNotifications"] = widget.get_active()

    def __checkbuttonIcon_toggled(self, widget):
        self._settings_dict["showIcon"] = widget.get_active()

    def __checkbuttonBlink_toggled(self, widget):
        self._settings_dict["blinkIcon"] = widget.get_active()

    def __on_checkbuttonUseProxy_toggled(self, widget):
        self._settings_dict["useProxy"] = widget.get_active()

    def __on_entryProxyAddress_changed(self, widget):
        self._settings_dict["proxyName"] = widget.get_text()

    def __on_entryProxyPort_changed(self, widget):
        self._settings_dict["proxyPort"] = int(widget.get_text())

#    def __on_entryProxyUserName_changed(self, widget):
#        self._settings_dict["proxyUser"] = widget.get_text()
#
#    def __on_entryProxyPassword_changed(self, widget):
#        self._settings_dict["proxyPassword"] = widget.get_text()

    def __on_comboboxProxyAuthentication_changed(self, widget):
        self._settings_dict["proxyAuthenticationType"] = widget.get_active()

    def __on_checkbuttonUseUploaderPass_toggled(self, widget, uploaderName):
        settingName = self._settings_class.getSettingNameForUsingUploaderPassword(uploaderName)
        self._settings_dict[settingName] = widget.get_active()

    def __on_checkbuttonISUse_toggled(self, widget):
        self._settings_dict["useISPassword"] = widget.get_active()

    def __on_checkbuttonRSUse_toggled(self, widget):
        self._settings_dict["useRSPassword"] = widget.get_active()

    def __comboboxPrefferedUploader_changed(self, widget, fileType, uploaders):
        """widget - combobox which value had been changed
        fileType - type of file that combobox was representing(fe:jpg)
        uploaders - list of combobox values
        """
        index = widget.get_active()
        value = uploaders[index]
        self._settings_dict["preferredUploaders"][fileType] = value

def _save_uploader_credentials(account_credentials, settings):
    """saves given accounts info to settings"""
    for pluginName, entries in account_credentials:
        usernameEntry = entries[0]
        passwordEntry = entries[1]
        settings.setUploaderCredentials(pluginName, usernameEntry.get_text(), passwordEntry.get_text())

if __name__ == "__main__":
    settings = Settings_GTK()
    gtk.main()

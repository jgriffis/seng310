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

__author__="Sebastian Kacprzak <naicik at gmail.com>"
__date__ ="$2009-12-15 08:22:11$"


from Singleton import Singleton
dbExists = False
db = None
try:
    from DB import DB
    db = DB()
    dbExists = True
except ImportError:
    pass
    

class Settings(object):
    """gives PyShare settings.
    If database exists gives settings from it, otherwise returns default values"""
    __metaclass__ = Singleton
    _settingsDefault = {
        #PyShare_GTK settings
        "maximumHeight" : 512, # maximum window height - window will grow with number of files, but will never pass this value
        "thumbnailSize" : 96, # if image is not square ratio will be keeped
        "showNotifications" :  True, # True / False
        "showIcon" :  True, #  True / False show icon in notification area
        "blinkIcon" :  True, #  True / False blink icon in notification area after uploads
        "allowOneInstanceOnly" :  True, # if True all files will be sended by one window
        "clipboardType" :  "CLIPBOARD", # "CLIPBOARD" / "PRIMARY" clipboard - paste by ctrl+v or right click, primary - paste by middle click
        "maxConnections" : 2, # max number of concurrent uploads
        #sendScreenshot settings
        "fileType" : 'png', # png, jpg, tiff or bmp. Suggested: png or jpg(lower quality, but usually lower size) Default: png
        "fileSize" : 1,  #  from 1(lowest size, but huge quality loss when using jpg or longer compress time for png) to 100(huge size). For png there could be also 0 witch will use external optipng to compress png file even more if optipng is installed on the system. Default: 1 for png, 75 for jpg
        "useProxy" : False,
        "proxyName" : "",
        "proxyPort" : 8080,
        "proxyUseCredentials" : False, # if true gnome keyring will be asked about user and password
        "proxyAuthenticationType" : 1, # None:0, Basic:1, Digest:2, GSS-Negotiate:3, NTLM:4, Any:5, Any safe:6
        "preferredUploaders": {
                "jpg":"Imageshack",#jpg and jpeg should be handled same way
                "bmp":"Imageshack",
                "gif":"Imageshack",
                "png":"Imageshack", 
                "tif":"Imageshack",#tif and tiff should be handled same way
                "pdf":"Imgur",
                "xcf":"Imgur",
                "apng":"Imgur",
                "*":"Rapidshare"
            }
    }
    __settings = None
    __keyringName = "Pyshare"

    def getDefaultSettings(self):
        return self._settingsDefault

    def getSettings(self):
        """returns all stored settings"""
        return self.__settings

    def saveSettingsToDB(self):
        self._saveSettingsToDB(self.__settings)

    def _saveSettingsToDB(self, settings):
        """saves settings in current form to database"""
        assert dbExists
        db.setSettings(settings)

    def getAllowOneInstanceOnly(self):
        return self.__settings["allowOneInstanceOnly"]
    def getMaximumHeight(self):
        return self.__settings["maximumHeight"]
    def getThumbnailSize(self):
        return self.__settings["thumbnailSize"]
    def getShowNotifications(self):
        return self.__settings["showNotifications"]
    def getShowIcon(self):
        return self.__settings["showIcon"]
    def getBlinkIcon(self):
        return self.__settings["blinkIcon"]
    def getClipboardType(self):
        return self.__settings["clipboardType"]
    def getMaxConnections(self):
        return self.__settings["maxConnections"]
    def getFileType(self):
        return self.__settings["fileType"]
    def getFileSize(self):
        return self.__settings["fileSize"]
    def getUseProxy(self):
        return self.__settings["useProxy"]
    def getProxyName(self):
        return self.__settings["proxyName"]
    def getProxyPort(self):
        return self.__settings["proxyPort"]
    def getPreferredUploaders(self):
        return self.__settings["preferredUploaders"]

    def getProxyCredentials(self):
        if self.__settings["proxyUseCredentials"]:
            from Keyring import Keyring
            key = Keyring(self.__keyringName)
            return key.get_credentials("proxy")
        return None
    def setProxyCrednetials(self,user,pw):
        if user:
            from Keyring import Keyring
            key = Keyring(self.__keyringName)
            key.override_credentials((user, pw), "proxy")
            self.__settings["proxyUseCredentials"] = True
        else:
            self.__settings["proxyUseCredentials"] = False
        del pw
        del user

    def getSettingNameForUsingUploaderPassword(self,uploaderName):
        return "usePasswordFor"+uploaderName

    def getCredentials(self, credentialsName):
        if(credentialsName == "proxy"):
            return self.getProxyCredentials()
        else:
            return self.getUploaderCredentials(credentialsName)

    def getUploaderCredentials(self, uploaderName):
        """returns either pair of username and password for given uploader
        or None if credentials are not found or not in use
        uploaderName - name of plugin that will use credentials"""
        from Keyring import Keyring
        key = Keyring(self.__keyringName)
        return key.get_credentials(uploaderName, "http")

    def setUploaderCredentials(self, uploaderName, user, pw):
        settingName = self.getSettingNameForUsingUploaderPassword(uploaderName)
        from Keyring import Keyring
        key = Keyring(self.__keyringName)
        key.override_credentials((user, pw), uploaderName, "http")
        if not user:
            # hostings don't allow for empty username
            self.__settings[settingName] = False
        del pw
        del user

    def getProxyAuthenticationType(self):
        return self.__settings["proxyAuthenticationType"]

    def _load_settings(self):
        """try to load settings from database.

        If db don't exist uses default values and writes defaults to database
        If db exist but settings are incorrect(probably because program version
        missmatch) merges correct database settings with defaults and writes them to database.
        return merged settings

        """
        assert dbExists
        result = {}
        databaseSettings = db.getSettings()
        if not databaseSettings:
            result = self._settingsDefault # use defaults
        else:
            # Merge defaults with settings.
            # If setting exist in both defaults and database
            # use value from database
            result = dict(self._settingsDefault, **databaseSettings)  # creates dictionary with all entries from database and lacking from defaults
            if "preferredUploaders" in databaseSettings:
                result["preferredUploaders"] = dict(self._settingsDefault["preferredUploaders"], **databaseSettings["preferredUploaders"])
        result = _fix_preffered_uploaders_if_needed(result)
        settings_changed = databaseSettings != result
        if settings_changed:
            self._saveSettingsToDB(result)
        return result


    def putUseUploadersCredentialsIntoSettings(self, pluginsWithPasswords):
        """Fills settings with lacking usePasswordForUploader

        put 'usePasswordFor' = plugin.PASSWORD_REQUIRED in settings
        for each plugin that can use credentials, that did not have
        value for this setting stored.
        If plugin requires password old setting will be overriden
        to use password.

        """
        for plugin in pluginsWithPasswords:
            settingName = self.getSettingNameForUsingUploaderPassword(plugin.NAME)
            if not settingName in self.__settings:
                self.__settings[settingName] = plugin.PASSWORD_REQUIRED
            elif plugin.PASSWORD_REQUIRED:
                # override settings if plugin demand password
                self.__settings[settingName] = plugin.PASSWORD_REQUIRED

    def __init__(self):
        settings = self._load_settings()
        self.__settings = settings


def _fix_preffered_uploaders_if_needed(settings):
    """change preffered uploaders if they have list as values

    return dictionary of correct uploaders
    this function is for transition between PyShare o.5.* to 0.6

    """
    preferredUploaders = settings["preferredUploaders"]
    for type, uploader in preferredUploaders.items():
        if isinstance(uploader, list):
            preferredUploaders[type] = uploader[0]
    return settings

#uploaders
#this file handles plugins choosing

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
__date__ ="$2009-11-27 21:08:44$"

from Settings import Settings
#from plugins import Centrezone_it, Imagebam_com
from Twitpic_com import Twitpic_com
from Imageshack_us import Imageshack_us
from Rapidshare_com import Rapidshare_com
from Imgur_com import Imgur_com

#dictionary of all active plugins
_PLUGINS = {
    Imageshack_us.NAME: Imageshack_us,
    Twitpic_com.NAME: Twitpic_com,
    Rapidshare_com.NAME: Rapidshare_com
}

def _initFiletypeHandlers(plugins):
    """creates a dictionary containg filetypes as keys
    and names of plugins capable of uploading them as values"""
    #dictionary of plugins that can upload only some file types
    filetype_handlers = {}
    #list of plugins that can upload any file type
    universal_handlers = []
    for plugin in plugins.values():
        accepted_file_types = plugin.ACCEPTED_FILE_TYPES
        pluginName = plugin.NAME
        for filetype in accepted_file_types:
            if filetype is "*":
                universal_handlers.append(pluginName)
                continue
            if filetype not in filetype_handlers:
                filetype_handlers[filetype] = []
            filetype_handlers[filetype].append(pluginName)
    return filetype_handlers, universal_handlers

#FILETYPE_HANDLERS - dictionary of plugins that can upload only some file types
#UNIVERSAL_HANDLERS - list of plugins that can upload any file type
FILETYPE_HANDLERS, UNIVERSAL_HANDLERS = _initFiletypeHandlers(_PLUGINS)

def _initPluginsWithPasswords(plugins):
    """returns list of plugins that can use passwords,
    and informs settings about them"""
    pluginsWithPasswords = []
    for plugin in plugins.values():
        if plugin.CAN_USE_PASSWORD:
            pluginsWithPasswords.append(plugin)
    Settings().putUseUploadersCredentialsIntoSettings(pluginsWithPasswords)
    return pluginsWithPasswords
#list of plugins that can store passwords
PLUGINS_WITH_PASSWORDS = _initPluginsWithPasswords(_PLUGINS)

def getPluginByHostingName(name):
    """returns plugin with given name"""
    return _PLUGINS[name]

def getUploader(file):
    preferredUploaders = Settings().getPreferredUploaders()
    extension = file.split('.')[-1].lower()
    filetype = __getFiletype(extension)
    if filetype in preferredUploaders.keys():
        prefferedUploader = preferredUploaders[filetype]
    else:
        prefferedUploader = preferredUploaders["*"]
    return getPluginByHostingName(prefferedUploader)

def __getFiletype(extension):
    if extension == "jpeg":
        extension = "jpg"
    elif extension == "tiff":
        extension = "tif"
    return extension


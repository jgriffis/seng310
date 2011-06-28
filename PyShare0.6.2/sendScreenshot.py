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

from os import system

from Settings import Settings
set = Settings()
import gettext

#gettext.bindtextdomain('sendScreenshot', 'translations')
#gettext.textdomain('sendScreenshot')
#_ = gettext.gettext
gettext.install('sendScreenshot', 'translations')



def sendScreenshot(windowScreenshot=False):
    from PyShare_GTK import uploadFilesGUI
    try:
        screenshotPath = getScreenshot(windowScreenshot)
        files = [screenshotPath,]
        uploadFilesGUI(files)
    except Exception, e:
        from PyShare_GTK import importErrorDialog
        importErrorDialog(e)


def getScreenshot(windowScreenshot):
    """takes screenshot and send it to Imageshack
    if windowScreenshot is set to True sends screenshot of window wich user clicks
    returns path to screenshot"""
    fileType = set.getFileType()
    fileSize = set.getFileSize()
    if fileType == 'png' and fileSize == 0:
       if system("command -v optipng"): # checks exitstatus to indicate if optipng is installed on the system
          raise Exception(_("Best png fileSize requires optipng. Try to install optipng package, or set fileSize to bigger value"))

    if system("command -v scrot"):
       raise Exception(_("This script needs scrot. Try to install scrot package."))

    tmpFilePath = '/tmp/STIScreenshot.' + fileType
    flags = ''
    if not (fileType == 'png' and fileSize == 0):
      flags += ' -q '+ str(fileSize) + ' '
    if windowScreenshot:
      flags += ' -s ' # take screenshot of clicked window
    #system('import -window root ' + tmpFilePath) # import have problem with compiz transparency
    system('scrot ' + flags  + tmpFilePath)
    if (fileType == 'png' and fileSize == 0):
      system('optipng ' + tmpFilePath) # compress file using optipng
    return tmpFilePath


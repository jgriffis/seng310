#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2010>  <Sebastian Kacprzak> <naicik |at| gmail |dot| com>
#    Copyright (C) <2010>  <Krzysztof Chrobak> <krzycho |dot| ch |at| gmail |dot| com>

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

__author__="Krzysztof Chrobakk <krzycho.ch at gmail.com>"
__date__ ="$2010-03-12 12:43:31$"

import gettext
gettext.bindtextdomain('cliHelper', '.')
gettext.textdomain('cliHelper')
_ = gettext.gettext

from progressBarCLI import ProgressBarCLI

def printProgressToCLI(fileNumber, download_t, download_d, upload_t, upload_d):
    """print progress bar to CL"""
    #TODO: writeme - allow flag argument that prints some sane CLI progressbar
    pbar=ProgressBarCLI(upload_t)
    pbar.update(upload_d)

def printLink(links, fileNumber, file):
    """prints links to CL"""
    print _("file ") + file + _(" uploaded:")
    for link in links:
        print link
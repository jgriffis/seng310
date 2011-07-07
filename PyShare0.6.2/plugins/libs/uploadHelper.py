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


def createLinks(fileDownloadLink, fileName = None, imageLink = None, thumbLink=None):
    links=[fileDownloadLink]
    types=None
    if not fileName:
        fileName = fileDownloadLink
    else:
        import os
        fileName = os.path.basename(fileName) # use only fileName, not a long path
    if imageLink:
        links.insert(0, imageLink) # Direct
        types = ['Direct', 'IM']
    else:
        types = ['IM']
    return links, types, [fileDownloadLink, thumbLink, imageLink]

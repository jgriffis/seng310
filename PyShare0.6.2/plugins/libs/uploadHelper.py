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
        links.append("[URL=" + fileDownloadLink + "][IMG]" + imageLink + "[/IMG][/URL]") # Forum
        links.append("[URL=" + fileDownloadLink + "][IMG=" + imageLink + "][/IMG][/URL]") # Alt Forum
        links.append("<a target='_blank' href='" + fileDownloadLink + "'><img src='" + imageLink + "' border='0'/></a>") # HTML
        links.append(imageLink) # Direct
        if not thumbLink:
            thumbLink = imageLink # thumb was not generated, use image as a thumb
        links.append( "[URL=" + fileDownloadLink + "][IMG]" + thumbLink + "[/IMG][/URL]" ) # Forum Thumb
        links.append( "[URL=" + fileDownloadLink + "][IMG=" + thumbLink + "][/IMG][/URL]" ) # Alt Forum Thumb
        links.append( "'<a target='_blank' href='" + fileDownloadLink + "'><img src='" + thumbLink + "' border='0'/></a>" ) # HTML Thumb
        links.append("http://yfrog.com/?url=" + imageLink) # Twitter Link
        types = ['IM', 'Forum', 'Alt Forum', 'HTML', 'Direct', 'Forum Thumb', 'Alt Forum Thumb', 'HTML Thumb', 'Twitter Link']
    else:
        links.append("[URL=" + fileDownloadLink + "]" + fileName + "[/URL]") # Forum
        links.append("[URL=" + fileDownloadLink + "]" + fileName + "[/URL]") # Alt Forum
        links.append("<a target='_blank' href='" + fileDownloadLink + "'>" + fileName + "</a>") # HTML
        types = ['IM', 'Forum', 'Alt Forum', 'HTML']
    return links, types, [fileDownloadLink, thumbLink, imageLink]

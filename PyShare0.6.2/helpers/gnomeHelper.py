#!/usr/bin/env python

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

__author__="Sebastian Kacprzak <naicik at gmail.com>"
__date__ ="$2009-11-28 17:39:09$"

import os


def getPyShareHomeDirectory():
    """returns string with pyshare settings folder"""
    dir = os.path.expanduser("~") + '/.pyshare/' #TODO: replace with system specyfic slashes
    if not os.path.exists(dir):
        os.makedirs(dir)
        os.makedirs(dir+'cache/')
    return dir











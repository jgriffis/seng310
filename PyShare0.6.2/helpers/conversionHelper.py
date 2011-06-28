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

from datetime import datetime

def convert_bytes(number_of_bytes):
    bytes = float(number_of_bytes)
    if bytes >= 1048576:
        megabytes = bytes / 1048576
        filesize = "%.2fMB" % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        filesize = "%.2fKB" % kilobytes
    else:
        filesize = "%.2fb" % bytes
    return filesize

def convert_date(date):
    datestring, microseconds = date.split(".", 1)
    dt = datetime.strptime(datestring,"%Y-%m-%d %H:%M:%S")
    return dt.strftime("%d-%m-%Y %H:%M")

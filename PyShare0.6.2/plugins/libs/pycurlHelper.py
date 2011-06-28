#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2010>  <Sebastian Kacprzak> <naicik |at| gmail |dot| com>

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
__date__ ="$2010-03-11 21:56:37$"

import pycurl
from Settings import Settings
set = Settings()

def getPycurlProxyAuthenticationType():
    authType = set.getProxyAuthenticationType()
    if authType == 0:#"None":
        return pycurl.HTTPAUTH_NONE # nothing
    if authType == 1:#"Basic":
        return pycurl.HTTPAUTH_BASIC # Basic (default)
    if authType == 2:#"Digest":
        return pycurl.HTTPAUTH_DIGEST # Digest
    if authType == 3:#"GSS-Negotiate":
        return pycurl.HTTPAUTH_GSSNEGOTIATE # GSS-Negotiate
    if authType == 4:#"NTLM":
        return pycurl.HTTPAUTH_NTLM # NTLM
    if authType == 5:#"Any":
        return pycurl.HTTPAUTH_ANY # all fine types set
    if authType == 6:#"Any safe":
        return pycurl.HTTPAUTH_ANYSAFE
#    if authType == :
#        return pycurl.HTTPAUTH_AVAIL #
#    if authType == :
#        return pycurl.HTTPAUTH #



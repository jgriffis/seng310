#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (C) <2007>  <Sebastian Rittau ><http://www.rittau.org/blog/20070726-01>
#    modified by <Sebastian Kacprzak>

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

from Singleton import Singleton
import gnomekeyring as gkey

class Keyring(object):
    __metaclass__ = Singleton

    def __init__(self, name):
        """name - application name"""
        self.__name = name
        self.__keyring = gkey.get_default_keyring_sync()
        # for transiton only. Remove somwhere around april 2011
        self._override_old_passwords({"Rapidshare": "http",
                                    "Imageshack": "http",
                                    "Twitpic": "http",
                                    "proxy": None})

    def get_credentials(self, server, protocol=None):
        try:
            attrs = {"server": server}
            if protocol:
                attrs["protocol"] = protocol
            items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
            return (items[0].attributes["user"], items[0].secret)
        except gkey.NoMatchError:
            return None

    def set_credentials(self, (user, pw), server, protocol=None):
        attrs = {
            "user": user,
            "server": server,
            "application" : self.__name
        }
        if protocol:
            attrs["protocol"] = protocol

        display_name = self.__name + " " + server
        gkey.item_create_sync(gkey.get_default_keyring_sync(),
                gkey.ITEM_NETWORK_PASSWORD, display_name, attrs, pw, True)

    def override_credentials(self, (user, pw), server, protocol=None, attrs=None):
        """save given credentials on top of existing ones

        all old credentials that match given server,
        application name and optionaly protocol will be purged

        """
        if not attrs:
            attrs = {"server": server, "application" : self.__name}
        try:
            if protocol:
                attrs["protocol"] = protocol
            try:
                items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
                for item in items:
                    gkey.item_delete_sync(None, item.item_id)
            except gkey.NoMatchError:
                pass #nothing to delete
            self.set_credentials((user, pw), server, protocol)
            return True
        except gkey.DeniedError:
            return False

    def _new_passwords_exists(self):
        """check if there is any password saved in new format

        if there are any credentaials with application set
        then return true
        method for transtion between versions <0.62 to 0.62

        """

        try:
            attrs = {"protocol": "http", "application" : self.__name}
            items = gkey.find_items_sync(gkey.ITEM_NETWORK_PASSWORD, attrs)
            return len(items) > 0
        except gkey.DeniedError:
            return False
        except gkey.NoMatchError:
            return False


    def _override_old_passwords(self, servers_and_protocols):
        if self._new_passwords_exists():
            return
        for server, protocol in servers_and_protocols.items():
            credentials = self.get_credentials(server, protocol)
            if credentials:
                user, pw = credentials
                self.override_credentials((user, pw), server, protocol, {"server": server})


#from Keyring import Keyring
#    key = Keyring("Pyshare","rapidshare.com","http")
#    print key.get_credentials()
#    key.set_credentials()


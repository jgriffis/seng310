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

from thread import start_new_thread

import dbus
import dbus.glib
import dbus.service
import dbus.mainloop.glib
import gobject
from threading import Thread

busName = 'net.launchpad.pyshare'
objectPath = '/launchpad/net/pyshare'
# register in mainloop to avoid possible race condition and crash
# when gnome keyring is asked for credentaials by find_items_sync
# which is not thread safe
dbus.mainloop.glib.threads_init()

class __AllowOnlyOneInstance(dbus.service.Object, Thread):

    def __init__(self, callback):
        """throws KeyError if instance was already registered"""
        self.callback = callback
        objectBus = dbus.service.BusName(busName, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, objectBus, objectPath)

    def listen(self):
        gobject.threads_init()
        dbus.glib.init_threads()
        gobject.MainLoop().run()

    @dbus.service.method(busName)
    def sendFiles(self, files):
        """convert dbus array to string list and pass it to self.callback"""
        #dbus array may look like this dbus.Array([dbus.String(u't.png'), dbus.String(u't2.png')], signature=dbus.Signature('s'), variant_level=1)
        i = 0
        result = []
        while i < len(files):
            result.append(str(files[i]))
            i += 1
        self.callback(result)


def instanceExists(callback):
    """tries to register instance of pyshare"""
    bus = dbus.SessionBus()
    names = bus.list_names()
    if busName in names:
        return True
    else:
        try:
            instance = __AllowOnlyOneInstance(callback)
            start_new_thread(instance.listen, ())
        except KeyError:
            print "key error"  # maybe same instance tried to reserve dbus twice? show new window just to be sure
            pass
    return False


def sendFilesToInstance(files):
    if files: # if there are no files don't bother poking other instance - empty list is not correct dbus argument either
        bus = dbus.SessionBus()
        sendingService = bus.get_object(busName, objectPath)
        sendFiles = sendingService.get_dbus_method('sendFiles', busName)
        sendFiles(files)

if __name__ == '__main__':
    def tmp(files):
        print files
    assert instanceExists(tmp) == False # test only
    #assert instanceExists(lambda x: 2) == True # test only
    print "asserts succseded"
    sendFilesToInstance(["t2.png", "t.png"])
    print "after send files"


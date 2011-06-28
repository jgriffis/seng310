#!/usr/bin/env python

from Keyring import Keyring
ins = Keyring("Pyshare")
sap = {"Rapidshare": "http",
    "Imageshack": "http",
    "Twitpic": "http",
    "proxy": None}
ins.override_old_passwords(sap)


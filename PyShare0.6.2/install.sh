#!/usr/bin/env sh

#this script will link PyShare_GTK, sendFiles, sendDesktopScreenshot and sendFiles
#to nautilius script folder

PWD="`pwd`"

ln -s "${PWD}/PyShare_GTK.py" ~/.gnome2/nautilus-scripts/PyShare_GUI
ln -s "${PWD}/sendFiles" ~/.gnome2/nautilus-scripts/PyShare_sendFiles
ln -s "${PWD}/sendDesktopScreenshot" ~/.gnome2/nautilus-scripts/PyShare_SendDesktopScreenshot
ln -s "${PWD}/sendWindowScreenshot" ~/.gnome2/nautilus-scripts/PyShare_sendWindowScreenshot



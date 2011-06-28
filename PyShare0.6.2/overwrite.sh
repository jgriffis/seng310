#!/usr/bin/env sh

#this script will link PyShare_GTK, sendFiles, sendDesktopScreenshot and sendFiles
#to nautilius script folder. It will overwrite old files if they exists

PWD="`pwd`"

ln -s "${PWD}/PyShare_GTK.py" ~/.gnome2/nautilus-scripts/PyShare_GTK -f
ln -s "${PWD}/sendFiles" ~/.gnome2/nautilus-scripts/sendFiles -f
ln -s "${PWD}/sendDesktopScreenshot" ~/.gnome2/nautilus-scripts/sendDesktopScreenshot -f
ln -s "${PWD}/sendWindowScreenshot" ~/.gnome2/nautilus-scripts/sendWindowScreenshot -f



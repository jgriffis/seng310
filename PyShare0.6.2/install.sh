#!/bin/bash

#/usr/bin/env sh

#this script will link PyShare_GTK, sendFiles, sendDesktopScreenshot and sendFiles
#to nautilius script folder

__PWD="`pwd`"

ln -s "${PWD}/PyShare_GTK.py" ~/.gnome2/nautilus-scripts/PyShare_GUI
ln -s "${PWD}/sendFiles" ~/.gnome2/nautilus-scripts/PyShare_sendFiles
ln -s "${PWD}/sendDesktopScreenshot" ~/.gnome2/nautilus-scripts/PyShare_SendDesktopScreenshot
ln -s "${PWD}/sendWindowScreenshot" ~/.gnome2/nautilus-scripts/PyShare_sendWindowScreenshot

#following prompts user if they want to create a launcher on desktop
echo "Create Launcher on Desktop? (y/n)"
read LAUNCH

if [ $LAUNCH == "y" ];
then
	cd ~/Desktop
	cp ${__PWD}/launcher.generic PyShare.desktop
	echo "Exec=${__PWD}/PyShare_GTK.py" >> PyShare.desktop
	echo "Icon=${__PWD}/icon.png" >> PyShare.desktop
	chmod +x PyShare.desktop
fi

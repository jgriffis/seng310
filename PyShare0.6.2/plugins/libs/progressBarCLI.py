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

from os import popen
import sys

class ProgressBarCLI():
	def __init__(self, maxval):
		self.maxval=maxval
		self.rows, self.columns = popen('stty size', 'r').read().split()
	def update(self, currentval):
		sys.stdout.write(('\r'))
		self.printPercentage(currentval)
		self.printBar(currentval)
		sys.stdout.write("   " + str(currentval))
		sys.stdout.flush()
	def printPercentage(self,currentval):
		percentstring='%3d%%' % round(currentval *100/self.maxval)
		sys.stdout.write(str(percentstring))
	def printBar(self,currentval):
		barsize=int(self.columns) - 50;
		numberFill=int(barsize*currentval/self.maxval)
		sys.stdout.write("[" + (numberFill-1)*'=' + ">" + (barsize-numberFill)*' ' + "]")
        def printETA(self,currentval):
            #TODO
            pass
        def printUploadSpeed(self):
            #TODO
            pass

if __name__ == "__main__":
    import time
    p = ProgressBarCLI(100)
    for i in range(101):
        p.update(int(i))
        time.sleep(0.1)
    sys.stdout.write(('\n'))

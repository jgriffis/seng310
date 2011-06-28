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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import datetime
import pickle

import sqlite3

from helpers.gnomeHelper import getPyShareHomeDirectory
from Singleton import Singleton

historypathfile = getPyShareHomeDirectory()+"pyshare.db"


class DB():
      __metaclass__ = Singleton
      def __init__(self):
            if not os.path.exists(historypathfile):
                    self.createDbFile()
                    self.createCursor()
                    self.addInitialData()
            else:
                    self.connection=sqlite3.connect(historypathfile,check_same_thread=False)
                    self.createCursor()


      def createDbFile(self):
        """create database file in pyshare home directory if not exists"""
        #connect to database file in application home directory
	self.connection=sqlite3.connect(historypathfile,check_same_thread=False)
	cc=self.connection.cursor()
        #create table with link to images
	cc.execute('''create table file(id INTEGER PRIMARY KEY AUTOINCREMENT, hosting_id INTEGER, directlink TEXT, thumblink TEXT, adlink TEXT, upload_date TEXT, filename TEXT, filesize INTEGER, extension TEXT, mimetype TEXT)''')
	self.connection.commit()
        #create table with inforamtion about hostings
        cc.execute('''create table hosting(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, url TEXT, tosurl TEXT)''')
        self.connection.commit()
        #create table with settings
        cc.execute('''create table setting(name TEXT, value TEXT)''')
        self.connection.commit()
	cc.close()

      def createCursor(self):
	self.cursor=self.connection.cursor()

      def addInitialData(self):
        self.addHosting("Imageshack", "http://imageshack.us/", "http://reg.imageshack.us/content.php?page=rules")
        self.addHosting("Rapidshare", "http://rapidshare.com/", "http://rapidshare.com/agb.html")
        self.addHosting("Twitpic", "http://twitpic.com", "http://twitpic.com/terms.do")
        #self.addHosting("Centerzone", "http://upload.centerzone.it/", "http://upload.centerzone.it/info.php?act=rules")
        #self.addHosting("Imagebam","http://www.imagebam.com/","http://www.imagebam.com/nav/tos")
        #self.addHosting("Freeimagehosting", "http://www.freeimagehosting.net/upload.php", "http://www.freeimagehosting.net/rules.php")

      def addHosting(self, name, url, tosurl):
          """add new hosting to database"""
          self.cursor.execute('''insert into hosting (name, url, tosurl) values (?,?,?)''', (name, url, tosurl))
          self.connection.commit()

      def getHostingList(self):
          self.cursor.execute("""select * from hosting""")
          return self.cursor.fetchall()

      def getHostingListByDate(self,date):
          self.cursor.execute("""select h.name from file i join hosting h on i.hosting_id=h.id where strftime('%Y-%m-%d', upload_date)='""" + date +  """' group by i.hosting_id """)
          return self.cursor.fetchall()

      def getUploadDate(self):
          self.cursor.execute("""select strftime('%Y-%m-%d', upload_date) from file group by strftime('%Y%m%d', upload_date)""")
          return self.cursor.fetchall()

      def addImage(self, hosting_name, directlink, thumblink, adlink, filename, filesize, extension, mimetype):
          self.cursor.execute("""select * from hosting where (name=?) ;""", (hosting_name,))
          hosting_id=self.cursor.fetchone()[0]
          #insert to database info about imagefile
          self.cursor.execute("""insert into file (hosting_id, directlink, thumblink, adlink, upload_date, filename, filesize, extension, mimetype) values (?,?,?,?,?,?,?,?,?)""",
          (hosting_id, directlink, thumblink, adlink, datetime.datetime.now(), filename, filesize, extension, mimetype ))
          self.connection.commit()

      def addFile(self, hosting_name, directlink, thumblink, adlink, filename, filesize, extension, mimetype):
          self.cursor.execute("""select * from hosting where (name=?) ;""", (hosting_name,))
          hosting_ids = self.cursor.fetchone()
          # insert hosting info if it not exist
          if hosting_ids == None:
              self.addHosting(hosting_name, "", "")
              self.cursor.execute("""select * from hosting where (name=?) ;""", (hosting_name,))
              hosting_ids = self.cursor.fetchone()
          hosting_id = hosting_ids[0]
          #insert to database info about imagefile
          self.cursor.execute("""insert into file (hosting_id, directlink, thumblink, adlink, upload_date, filename, filesize, extension, mimetype) values (?,?,?,?,?,?,?,?,?)""",
          (hosting_id, directlink, thumblink, adlink, datetime.datetime.now(), filename, filesize, extension, mimetype ))
          self.connection.commit()

      def getImagesByHostingId(self):
          pass

      def getSettings(self):
          settings = None;
          self.cursor.execute("""SELECT * from setting where (name=?) """, ("settings",))
          object = self.cursor.fetchone()
          if object != None :
            settings = {}
            settings = pickle.loads(str(object[1]))
          return settings

      def setSettings(self, settings):
          str = pickle.dumps(settings)
          if self.getSettings() == None:
            self.cursor.execute("""insert into setting (name, value) values (?,?) """, ("settings", str))
          else:
            self.cursor.execute("""update setting set name =?, value =? where (name=?) """, ("settings", str, "settings"))
          self.connection.commit()

      def setDefaultHostings(self, hostings):
          str = pickle.dumps(hostings)
          if self.getSettings() == None:
            self.cursor.execute("""insert into setting (name, value) values (?,?) """, ("hostings", str))
          else:
            self.cursor.execute("""update setting set name =?, value =? where (name=?) """, ("hostings", str, "hostings"))
          self.connection.commit()

      def getDefaultHostings(self):
          hostings = None;
          self.cursor.execute("""SELECT * from setting where (name=?) """, ("hostings",))
          object = self.cursor.fetchone()
          if object != None :
            hostings = {}
            hostings = pickle.loads(str(object[1]))
          return hostings

      def getHostingByName(self,name):
          self.cursor.execute("""SELECT * from hosting where (name=?) ;""", (name,))
          return self.cursor.fetchone()
      
      def getImagesByUploadDate(self, date):
          self.cursor.execute("""SELECT * from file where (strftime('%Y-%m-%d', upload_date)=?)""", (date,))
          return self.cursor.fetchall()

      def getImagesByHostingName(self,name):
          hosting_id=self.getHostingByName(name)[0]
          self.cursor.execute("""SELECT * from file where (hosting_id=?) order by upload_date DESC;""",(hosting_id,))
          return self.cursor.fetchall()
          
      def getHostingById(self,id):
          self.cursor.execute("""SELECT * from hosting where (id=?) ;""", (id,))
          return self.cursor.fetchone()

      def getFileById(self,id):
          self.cursor.execute("""SELECT * from file where (id=?) ;""", (id,))
          return self.cursor.fetchone()

      def getLastUploaded(self, numberOfUploaded):
          self.cursor.execute("""SELECT * from file order by upload_date DESC LIMIT ?""", (numberOfUploaded,))
          return self.cursor.fetchall()

      def getImagesByUploadDateAndHosting(self, date, name):
          hosting_id=self.getHostingByName(name)[0]
          self.cursor.execute("""SELECT * from file where (hosting_id=?) and (strftime('%Y-%m-%d', upload_date)=?) order by upload_date DESC""", (hosting_id, date))
          return self.cursor.fetchall()

      def checkHosting(self,name):
          self.cursor.execute("""SELECT * from hosting where (name=?)""", (name,))
          try:
              hosting_id=self.cursor.fetchone()[0]
          except TypeError:
              return False
          if int(hosting_id) > 0 :
              return True
          return False

      def deleteFile(self,id):
          """remove information about file from history"""
          self.cursor.execute("""DELETE FROM file where (id=?) ;""",(id,))
          self.connection.commit()

      def removeHistory(self):
          self.cursor.execute("""DELETE FROM file ;""")
          self.connection.commit()

      def __close(self):
	self.connection.close()

if __name__ == '__main__':
    db=DB()

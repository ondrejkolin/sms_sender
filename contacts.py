#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Cause to drunkness here is to do list:
3) Dont know two beers made me unable to do some python coding
4) I love Wendy!
5) Dont use self.cur.commit() !!! #dont know where
6) Make history for message and number system
7) Get number automatic help on number entry from history & database
'''

import sqlite as lite
import sys
class Contacts:
    def __init__(self, db_name = "sms.db"):
        #Get or create databes
        self.con = None
        self.error = None
        try:
            self.con = lite.connect(db_name)
            self.cur = self.con.cursor()
        except lite.Error, e:
            print "Error %s:" % e.args[0]
            self.con = None
            self.error = e.args[0]
            return
        #testujeme spojeni
        #testujeme existenci tabulek
        #SELECT name FROM sqlite_master WHERE type='table' AND name='table_name';
        try:
            self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kontakty'")
            if (self.cur.rowcount < 1):
                print "Vytvářím tabulku kontakty"
                self.cur.execute("CREATE TABLE kontakty ('cislo' int(9), 'jmeno' string(50))")
                self.con.commit()
        except lite.Error, e:
            print "__init__ error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
    def add(self, number, name):
        if (self.error):
            print "Can not add due to error %s!" % self.error
            return None
        try:
            self.cur.execute("SELECT * FROM kontakty WHERE cislo = %d AND jmeno = '%s'" % (number, name))
            if (self.cur.rowcount != 0):
                return 1
            self.cur.execute("INSERT INTO kontakty VALUES (%d, '%s')" % (number, name))
            self.con.commit()
        except lite.Error, e:
            print "Add error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
        return 0
    def get(self, number):
        if (self.error):
            print "Can not get due to error %s!" % self.error
            return None
        try:
            self.cur.execute("SELECT * FROM kontakty WHERE cislo LIKE '%%%d%%'" % number)
            if (self.cur.rowcount == 0):
                return None
        except lite.Error, e:
            print "Get error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
    def get_num(self, name):
        if (self.error):
            print "Can not get_num due to error %s!" % self.error
            return None
        try:
            self.cur.execute("SELECT cislo FROM kontakty WHERE jmeno = '%s'" % name)
            if (self.cur.rowcount == 0):
                return None
        except lite.Error, e:
            print "Get error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
        return self.cur.fetchone()[0]
    def list_all(self):
        if (self.error):
            print "Can not get due to error %s!" % self.error
            return None
        try:
            self.cur.execute("SELECT * FROM kontakty")
            if (self.cur.rowcount == 0):
                return None
        except lite.Error, e:
            print "Get error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
        return self.cur.fetchall()
    def remove(self, number, name):
        if (self.error):
            print "Can not remove due to error %s!" % self.error
            return None
        try:
            self.cur.execute("DELETE FROM kontakty WHERE cislo=%d OR jmeno='%s'" % (number, name))
            self.con.commit()
        except lite.Error, e:
            print "Remove error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
    def number_used(self, number):
        if (self.error):
            print "Can not check number usage due to error %s" % self.error
            return None
        try:
            self.cur.execute("SELECT * FROM kontakty WHERE cislo = %d" % number)
        except lite.Error, e:
            print "Number usage error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
        if (self.cur.fetchone() != None):
            return True
        else:
            return False

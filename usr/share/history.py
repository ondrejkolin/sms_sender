#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite as lite
import sys
class History:
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
            self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historie'")
            if (self.cur.rowcount < 1):
                self.cur.execute("CREATE TABLE historie ('cislo' int(9), 'string' text)")
                print "Vytvářím tabulku historie"
                self.con.commit()
        except lite.Error, e:
            print "__init__ error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
    def add(self, number, text):
        if (self.error):
            print "Can not add due to error %s!:" % self.error
            return None
        try:
            self.cur.execute("INSERT INTO historie VALUES (%d, '%s')" % (number, text))
            self.con.commit()
        except lite.Error, e:
            print "Add error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
        return 0
    def remove(self, number, text):
        if (self.error):
            print "Can not remove due to error %s!:" % self.error
            return None
        try:
            self.cur.execute("DELETE FROM historie WHERE cislo='%d' AND string='%s'" % (number, text))
            self.con.commit()
        except lite.Error, e:
            print "Delete Error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
    def list_all(self):
        if (self.error):
            print "Can not get due to error %s!" % self.error
            return None
        try:
            self.cur.execute("SELECT * FROM historie")
            if (self.cur.rowcount == 0):
                return None
        except lite.Error, e:
            print "List_all error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
        result = []
        return self.translate(self.cur.fetchall())
    def clear(self):
        #known unefficiency due to using DELETE STATEMENT
        #Should be remade to DROP TABLE and CREATE TABLE
        if (self.error):
            print "Can not remove due to error %s!" % self.error
            return None
        try:
            self.cur.execute("DELETE FROM historie")
            self.con.commit()
        except lite.Error, e:
            print "Remove error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
        return True
    def uniq_numbers(self):
        if (self.error):
            print "Can not get due to error %s!" % self.error
            return None
        try:
            self.cur.execute("SELECT DISTINCT cislo FROM historie")
            if (self.cur.rowcount == 0):
                return None
        except lite.Error, e:
            print "List_all error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
        return self.translate(self.cur.fetchall())
    def disctinct_contacts(self):
        if (self.error):
            print "Can not get due to error %s!" % self.error
            return None
        try:
            self.cur.execute("SELECT DISTINCT cislo FROM historie WHERE cislo NOT IN (SELECT cislo FROM kontakty)")
            if (self.cur.rowcount == 0):
                return None
        except lite.Error, e:
            print "List_all error! Error msg %s" % e.args[0]
            self.error = e.args[0]
            return None
        return self.cur.fetchall()
    def translate(self, contacts):
        result = []
        for i in contacts:
            self.cur.execute("SELECT jmeno FROM kontakty WHERE cislo = '%d'" % i[0])
            jmeno = i[0]
            zprava = i[1]
            if (self.cur.rowcount != 0):
                jmeno = self.cur.fetchone()[0]
            result.append([jmeno, zprava])
        return result

        

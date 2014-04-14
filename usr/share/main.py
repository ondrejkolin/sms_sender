#!/usr/bin/python
# -*- Mode: Python; coding: utf-8;
import httplib
from os.path import expanduser
import urllib
import urllib2
import time
import gtk
import gtk.glade
import pango
from history import History
from contacts import Contacts
DATABASE = expanduser("~") + "/.sms.db"
def isInteger(number):
    ok = True
    try:
        int(number)
    except ValueError:
        ok = False
    return ok
class sms_sender:
    def __init__(self):
        self.history = History(db_name=DATABASE)
        self.contacts = Contacts(db_name=DATABASE)
        self.builder = gtk.Builder()
        self.builder.add_from_file("ui.glade")
        window = self.builder.get_object("window")
        self.message = self.builder.get_object("text")
        ###
        # Menu --> Connect
        self.builder.get_object("history").connect("activate", self.history_browsing)
        self.builder.get_object("contact").connect("activate", self.contact_browsing)
        ###
        window.show_all()
        window.connect("destroy", gtk.main_quit)
        ###
        cancel = self.builder.get_object("cancel")
        cancel.connect("clicked", gtk.main_quit)
        self.builder.get_object("exit").connect("activate", gtk.main_quit)
        ###
        ok = self.builder.get_object("ok")
        ok.connect("clicked", self.ok_clicked)
        ###
        self.check_box = self.builder.get_object("history_check")
        ###
        self.number = self.builder.get_object("number")
        self.number.connect("changed", self.on_number_changed)
        # Počítání znaků
        self.charcounter = self.builder.get_object("charcounter")
        self.message.get_buffer().connect("changed", self.on_message_changed)
        # Doplňování
        self.completion = gtk.EntryCompletion()
        self.store = gtk.TreeStore(str, str)
        self.completion.set_model(self.store)
        # Model creating
        self.completion.set_text_column(0)
        name_cell = gtk.CellRendererText()
        self.completion.pack_start(name_cell)
        self.completion.add_attribute(name_cell, 'text', 1)
        self.number.set_completion(self.completion)
        # About dialog
        self.about_dialog = self.builder.get_object("aboutdialog")
        self.builder.get_object("about").connect("activate", self.on_about_activate)
        # Progress dialog
        self.progress_dialog = self.builder.get_object("progressdialog")
        self.progress_ok = self.builder.get_object("progressok")
        self.progress_ok.connect("clicked", self.on_progressok_clicked)
        self.progress_bar = self.builder.get_object("progressbar")
        #gtkmainloop
        gtk.main()
    def send(self, target, what):
        test = 0
        ##Commend next row for production use
        test = 1
        if test == 1:
            return True
        print "Odesílám %s do %d" % (what, target)
        self.progress_dialog.hide()
        self.progress_dialog.show()
        self.progress_ok.set_sensitive(False)
        self.progress_bar.set_fraction(0.33)
        self.progress_bar.set_text("Kontaktuji web")
        timestamp = int(time.time())
        data = {
            'timestamp' : timestamp,
            'action'    : 'send',
            'sendingProfile1' : 11,
            'sendingProfile2' : 20,
            'sendingProfile3' : 32,
            'textsms' : what,
            'cislo-prijemce' : target
        }
        data = urllib.urlencode(data) 
        print('http://www.poslatsms.cz/', data)
        try:
            req = urllib2.Request('http://www.poslatsms.cz/', data)
            self.progress_bar.set_fraction(0.66)
            self.progress_bar.set_text("Odesílám data")
            response = urllib2.urlopen(req)
            the_page = str(response.read())
        except urllib2.error as e:
            print "error", e
            self.progress_bar.hide()
        print the_page
        if 'SMS zprávy přijaty k odeslání!' in the_page:
            self.progress_bar.set_text("Hotovo")
            self.progress_ok.set_sensitive(True)
            self.progress_bar.set_fraction(1.00)
            return True
        return False
    def on_message_changed(self, model):
        text = self.message.get_buffer().get_text(self.message.get_buffer().get_start_iter(), self.message.get_buffer().get_end_iter())
        chars = len(text)
        colour = "darkgreen"
        if chars > 625:
            self.message.get_buffer().set_text(text[:625])
            self.alert(self.message, "Překročena maximální délka zprávy!")
            text = self.message.get_buffer().get_text(self.message.get_buffer().get_start_iter(), self.message.get_buffer().get_end_iter())
            chars = len(text)
            colour = "red"
        label = "Napsáno %d/125" % (chars % 125)
        if chars > 125:
            label += "Počet zpráv %d/5" % (((chars - 1) / 125) + 1)
            
            preformat = '<span foreground="%s">' % colour
            postformat= '</span>'
            label = preformat + label + postformat
        self.charcounter.set_markup(label)
    def on_number_changed(self, model):
        cislo = True
        try:
            text = int(self.number.get_text())
        except ValueError:
            cislo = False
        self.store.clear()
        self.update_model(self.store, cislo)
    def update_model(self, model, number):
        #GET FROM CONTACTS
        try:
          for i in self.contacts.list_all():
              if number:
                  model.append(None, [i[0], i[1]])
              else:
                  model.append(None, [i[1], i[0]])
        except TypeError:
            print "No contacts stored"
        #GET FROM HISTORY
        try:
          for i in self.history.disctinct_contacts():
              model.append(None, [i[0], ""])
        except TypeError:
            print "History doesnt contain \"non-contact\" numbers"
        return model
    def info(self, msg):
        dialog = gtk.MessageDialog(None, 0,
                    gtk.MESSAGE_INFO,
                    gtk.BUTTONS_OK,
                    msg)
        choice = dialog.run()
        if choice != None:
            dialog.hide()      
    def alert(self, what, msg):
        #call alert from "what" with message "msg"
        dialog = gtk.MessageDialog(None, 0,
                    gtk.MESSAGE_WARNING,
                    gtk.BUTTONS_OK,
                    msg)
        choice = dialog.run()
        if choice != None:
            dialog.hide()
        if what:
            what.grab_focus()
    def on_about_activate(self, widget):
        self.about_dialog.run()
        self.about_dialog.hide()
    def history_browsing(self, widget):
        self.history_window = History_UI(parent=self)
        self.history_window.builder.get_object("history_dialog").show()
        if self.history_window.result:
          self.number.set_text(str(self.history_window.result[0]))
          self.message.get_buffer().set_text(self.history_window.result[1])
    def contact_browsing(self, widget):
        self.contact_window = Contacts_UI(parent=self)
        
    def ok_clicked(self, widget):
        if isInteger(self.number.get_text()):
            cislo = int(self.number.get_text())
            if (len(self.number.get_text()) != 9):
                self.alert(self.nubmer, "Číslo příjemce není 9 místné číslo")
                return 1
        else:
            cislo = self.contacts.get_num(self.number.get_text())
            if cislo == None:
                self.alert(self.number, "Uvedený kontakt nebyl nalezen")
                return 1
        text = self.message.get_buffer().get_text(self.message.get_buffer().get_start_iter(), self.message.get_buffer().get_end_iter())
        if (text == ""):
            self.alert(self.message, "Nelze odeslat prázdnou zprávu!")
            return 1
        while text <> "":
            if not(self.send(cislo, text[:125])):
                self.alert(None, "Chyba při odesílání! Změna enginu poskytovatele?")
                text = text[125:]
            else:
                # ukládání do historie
                if (self.check_box.get_active()):
                    self.history.add(cislo, text[:125])
                text = text[125:]
                self.message.get_buffer().set_text("")
                self.number.set_text("")
    def on_progressok_clicked(self,widget):
        self.progress_dialog.hide()
            
class Contacts_UI:
    def __init__(self, history=History(DATABASE), contacts=Contacts(DATABASE), parent=None):
        self.parent = parent
        self.result = None
        self.history = history
        self.contacts = contacts
        self.builder = gtk.Builder()
        self.builder.add_from_file("contacts.glade")
        self.window = self.builder.get_object("window")
        self.window.connect("destroy", self.on_close_clicked)
        self.builder.get_object("close").connect("clicked", self.on_close_clicked)
        self.builder.get_object("add").connect("clicked", self.on_add_clicked)
        self.builder.get_object("remove").connect("clicked", self.on_remove_clicked)
        self.treeview = self.builder.get_object("treeview1")
        self.store = gtk.TreeStore(str, str)
        self.treeview.set_model(self.store)
        self.treeview.set_model(self.update_model(self.store))
        columns = ["Jméno","Číslo"]
        for i in range(0,len(columns)):
          column = gtk.TreeViewColumn(columns[i])
          cell = gtk.CellRendererText()
          column.pack_start(cell, True)
          column.add_attribute(cell, 'text', i)
          self.treeview.append_column(column)
        self.treeview.set_cursor(0)
        self.window.show_all()
    def update_model(self, model):
        model.clear()
        try:
          for i in self.contacts.list_all():
              model.append(None, [i[1], i[0]])
        except TypeError:
              print "No contacts stored"
        return model
    def on_add_clicked(self, widget):
        dialog = self.builder.get_object("add_contact")
        name = self.builder.get_object("jmeno")
        cislo = self.builder.get_object("cislo")
        response = dialog.run()
        while response:
          dialog.hide()
          if not response:
              break
          #if correct - close
          if ((name.get_text() != "") and (len(cislo.get_text()) == 9) and (isInteger(cislo.get_text()))):
              if not self.contacts.number_used(int(cislo.get_text())):
                  break
              else:
                  error = gtk.MessageDialog(
                      type = gtk.MESSAGE_ERROR,
                      buttons = gtk.BUTTONS_CLOSE,
                      message_format = "Číslo již bylo použito!"
                  )
                  error.run()
                  error.destroy()
                  response = dialog.run()
                
          #if not give another try
          else:
              error = gtk.MessageDialog(
              type = gtk.MESSAGE_ERROR,
              buttons = gtk.BUTTONS_CLOSE,
              message_format = "Číslo musí mít 9 číslic a jméno musí být neprázdné"
              )
              error.run()
              error.destroy()
              response = dialog.run()
        dialog.hide()
        if response:
            self.contacts.add(int(cislo.get_text()), name.get_text())
            self.treeview.set_model(self.update_model(self.store))
            #If parent set i can regenerate database for whisperer
            self.parent.update_model(self.parent.store)
            self.update_model(self.store)
        name.set_text("")
        cislo.set_text("")
    def on_close_clicked(self, widget):
        self.window.hide()
    def on_remove_clicked(self, widget):
        cursor = self.treeview.get_cursor()[0]
        if cursor:
            cislo = self.treeview.get_model()[cursor[0]][1]
            jmeno = self.treeview.get_model()[cursor[0]][0]
        dialog = gtk.MessageDialog(
            buttons = gtk.BUTTONS_YES_NO,
            message_format = "Chcete smazat kontakt - '%s' s číslem '%s'" % (jmeno ,cislo)
        )
        response = dialog.run() + 9
        if response:
            self.contacts.remove(int(cislo), jmeno)
            self.treeview.set_model(self.update_model(self.store))
        dialog.destroy()
class History_UI:
    def __init__(self, history=History(DATABASE), contacts=Contacts(DATABASE), parent=None):
        self.result = None
        self.history = history
        self.contacts= contacts
        self.builder = gtk.Builder()
        self.builder.add_from_file("history.glade")
        self.window = self.builder.get_object("history_dialog")
        self.window.connect("destroy", self.on_cancel_clicked)
        self.builder.get_object("tool_ok").connect("clicked", self.on_ok_clicked)
        self.builder.get_object("tool_cancel").connect("clicked", self.on_cancel_clicked)
        self.builder.get_object("clear_history").connect("clicked", self.on_clear_history_clicked)
        self.builder.get_object("remove_button").connect("clicked", self.on_remove_button_clicked)
        self.ok = self.builder.get_object("ok")
        self.ok.connect("clicked", self.on_ok_clicked)
        self.cancel = self.builder.get_object("cancel")
        self.cancel.connect("clicked", self.on_cancel_clicked)
        self.treeview = self.builder.get_object("treeview")
        self.store = gtk.TreeStore(str, str)
        self.treeview.set_model(self.store)
        self.treeview.set_model(self.update_model(self.store))
        columns = ["Číslo","Text zprávy"]
        for i in range(0,len(columns)):
          column = gtk.TreeViewColumn(columns[i])
          cell = gtk.CellRendererText()
          column.pack_start(cell, True)
          column.add_attribute(cell, 'text', i)
          self.treeview.append_column(column)
        self.treeview.set_cursor(0)
    def update_model(self, model):
        model.clear()
        try:
          for i in self.history.list_all():
              model.append(None, [i[0], i[1]])
        except TypeError:
              print "No history stored"
        return model
    def on_ok_clicked(self, widget):
        cursor = self.treeview.get_cursor()[0]
        if cursor:
            try:
                cislo = int(self.treeview.get_model()[cursor[0]][0])
            except ValueError:
                cislo = Contacts(db_name=DATABASE).get_num(self.treeview.get_model()[cursor[0]][0])
            text = self.treeview.get_model()[cursor[0]][1]
            self.result = [cislo, text]
        self.window.hide()
    def on_remove_button_clicked(self, widget):
        cursor = self.treeview.get_cursor()[0]
        if cursor:
            try:
                cislo = int(self.treeview.get_model()[cursor[0]][0])
            except ValueError:
                cislo = Contacts(db_name=DATABASE).get_num(self.treeview.get_model()[cursor[0]][0])
            text = self.treeview.get_model()[cursor[0]][1]
            dialog = gtk.MessageDialog(
                buttons = gtk.BUTTONS_YES_NO,
                message_format = "Chcete smazat z historie SMS na %d s textem %s" % (cislo, text)
                )
            response = dialog.run()
            if response:
                self.history.remove(cislo, text)
                self.update_model(self.store)
            dialog.destroy()
        
            

    def on_cancel_clicked(self, widget):
        self.window.hide()
    def on_clear_history_clicked(self, widget):
        dialog = gtk.MessageDialog(
            buttons = gtk.BUTTONS_YES_NO,
            message_format = "Chcete smazat veškerou historii, bez možnosti návratu?"
        )
        #+9 je tu proto, že mi dialog vrací "-8 na True" a "-9 na False"
        #Takže to je Workaround :D
        response = dialog.run() + 9
        if response:
          self.history.clear()
          self.update_model(self.store)
        dialog.destroy()

sms_sender()

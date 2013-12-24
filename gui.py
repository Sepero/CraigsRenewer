#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
import wx

TRAY_TOOLTIP = "ON: renew craigslistings"
TRAY_ICON = "renewericon.png"

""" Interface display
Popup dialog to register
DialogBox to enter accounts
Title
Check to renew listings every: days hours minutes # default 1days, ignore 0 - 0
Button: Renew Now
Close to taskbar: checkbox
Start when computer starts: checkbox
Contact info/website
# Add Register Link to unregistered versions (embed sale info)
Status: time remaining / account: renewing listings
"""

def create_menu_item(menu, label, func):
    item = wx.MenuItem(menu, -1, label)
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.AppendItem(item)
    return item

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame):
        super(TaskBarIcon, self).__init__()
        self.frame = frame
        self.set_icon(TRAY_ICON)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
    
    def CreatePopupMenu(self, event=None):
        menu = wx.Menu()
        create_menu_item(menu, 'Renew now', self.on_exit)
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu
    
    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)
    
    def on_left_down(self, event):
        if self.frame.IsShown():
            self.frame.Hide()
        else:
            self.frame.Show()
    
    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        self.frame.Destroy()

class CraigFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(CraigFrame, self).__init__(*args, **kwargs)
        
        panel = self.parent = wx.Panel(self, -1)
        
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.add_row1(), 0)
        box.Add(self.add_row2(), 1, wx.EXPAND)
        box.Add(self.add_row3(), 0, wx.ALIGN_RIGHT)
        box.Add(self.add_row4(), 0, wx.LEFT|wx.EXPAND, 10)
        box.Add(self.add_row5(), 0, wx.ALL|wx.ALIGN_RIGHT, border=2)
        box.Add(self.add_row6(), 0, wx.ALL|wx.ALIGN_RIGHT, border=2)
        #box.Add(item=text[1], proportion=1, flag=wx.ALIGN_RIGHT, border=0)
        panel.SetSizer(box)
        
        self.status_bar = self.CreateStatusBar()
        self.status_bar.SetStatusText("Loading...")
        
        #self.Bind(wx.EVT_CLOSE, self.on_close)
        #wx.EVT_BUTTON(self, 1, self.on_close)
        wx.EVT_CLOSE(self, self.on_close)
    
    def make_texts(self, labels, id=-1, **kwargs):
        texts = [ wx.StaticText(self.parent, id, x, **kwargs) for x in labels ]
        return texts
    def make_comboboxes(self, choice_matrix, id=-1, **kwargs):
        global logger
        comboboxes = []
        for x in choice_matrix:
            comboboxes.append(wx.ComboBox(self.parent, id, choices=x, **kwargs))
            comboboxes[-1].SetStringSelection(x[0])
        return comboboxes
    def add_to_box(self, box, items, **kwargs):
        for i in items:
            box.Add(i, **kwargs)
    def add_row1(self):
        text = self.make_texts(["Craigs Renewer"])[0]
        text.SetFont(wx.Font(20, wx.NORMAL, wx.NORMAL, wx.NORMAL))
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(text, 1, wx.ALL, 10)
        return box
    def add_row2(self):
        #row_text = [ "Try renew listings every:", "days", "hours", "minutes" ]
        row_text = [ "Try renew listings every:", "days", "hours" ]
        text = self.make_texts(row_text, style=wx.ALIGN_RIGHT)
        
        choice_matrix = [ map(str, range(61)) ] # days
        choice_matrix.append( map(str, range(24)) ) # hours
        #choice_matrix.append( map(str, range(24)) ) # minutes
        dropbox = self.make_comboboxes(choice_matrix, style=wx.CB_READONLY)
        for d in dropbox:
            d.SetMinSize(wx.Size(50,25))
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(text[0], 4, flag=wx.ALL, border=5)
        box.Add(dropbox[0])
        box.Add(text[1], 1)
        box.Add(dropbox[1])
        box.Add(text[2], 1)
        return box
    def add_row3(self):
        button = wx.Button(self.parent, -1, "Renew listings now")
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        #box.Add(wx.Button(parent, -1, "Renew listings now"), flag=wx.ALIGN_RIGHT, border=5)
        box.Add(button, flag=wx.ALL|wx.ALIGN_RIGHT, border=5)
        return box
    def add_row4(self):
        #text = self.make_texts(["Keep Craigs Renewer running in the system tray"])[0]
        checkbox = wx.CheckBox(self.parent, label="Keep Craigs Renewer running in the system tray", style=2)
        checkbox.SetValue(True)
        
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(checkbox, 1, flag=wx.ALL)
        return box
    def add_row5(self):
        link = wx.HyperlinkCtrl(self.parent, -1, label="visit website", url="sepero.pythonanywhere.com")
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(link)
        return box
    def add_row6(self):
        link = wx.HyperlinkCtrl(self.parent, -1, label="Register", url="sepero.pythonanywhere.com")
        box = wx.BoxSizer(wx.HORIZONTAL)
        box.Add(link)
        return box
    #def add_rowX(self):
        #box = wx.BoxSizer(wx.HORIZONTAL)
        #box.Add(wx.Button(self.parent, -1, 'B1'), 0, wx.ALL, 50)
        #box.Add(wx.Button(self.parent, -1, 'B2'), 1, wx.EXPAND)
        #box.Add(wx.Button(self.parent, -1, 'B3'), 0, wx.ALIGN_CENTER)
        #return box
    def on_create_tray(self, evt):
        self.tray = TaskBarIcon(self)
    
    def on_remove_tray(self, evt):
        self.tray.Destroy()
        self.tray = None
    
    def on_close(self, evt):
        # if not tray icon: then self.Destroy()
        self.Hide()


class CraigApp(wx.App):
    def OnInit(self):
        frame = CraigFrame(parent=None, id=-1, title='layout')#, size=(640, 480))
        frame.SetIcon(wx.IconFromBitmap(wx.Bitmap(TRAY_ICON)))
        frame.Show()
        self.tray = TaskBarIcon(frame)
        return True


def main():
    global logger
    logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    app = CraigApp()
    app.MainLoop()

main()

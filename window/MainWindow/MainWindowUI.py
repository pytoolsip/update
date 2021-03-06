# -*- coding: utf-8 -*-
# @Author: JimZhang
# @Date:   2018-10-09 22:41:23
# @Last Modified by:   JimDreamHeart
# @Last Modified time: 2019-03-16 13:46:29

import wx;
import os;
import base64;
import time;

from event.Instance import *; # local
from config.AppConfig import *; # local

class MainWindowUI(wx.Frame):
	"""docstring for MainWindowUI"""
	def __init__(self, parent, id = -1, title = "", pos = (0,0), size = (0,0), style = wx.DEFAULT_FRAME_STYLE, curPath = "", windowCtr = None):
		super(MainWindowUI, self).__init__(parent, id, title = title, pos = pos, size = size, style = style);
		self._className_ = MainWindowUI.__name__;
		self._curPath = curPath;
		self._projectPath = os.path.join(curPath, "..", "..");
		self.__windowCtr = windowCtr;

	def getCtr(self):
		return self.__windowCtr;

	def initWindow(self):
		self.initIcon();
		self.createViewCtrs();
		self.initWindowLayout();
		self.Centre();
		self.Show(True);
		pass;

	def initIcon(self):
		if "AppIcon" in PngConfig:
			img = base64.b64decode(PngConfig["AppIcon"].encode());
			fileName = f"temp_ptip_{time.time()}.ico";
			with open(fileName, 'wb') as f:
				f.write(img);
			self.SetIcon(wx.Icon(fileName, wx.BITMAP_TYPE_ICO));
			os.remove(fileName);

	def createViewCtrs(self):
		self.getCtr().createCtrByKey("GaugeView", params = {"size" : (self.GetSize()[0], -1), "label" : "正在请求更新数据..."}); # , parent = self, params = {}
		self.createTitle();
		self.createReverifyButton();
		self.createDetailTextCtrl();
		self.createCopyrightInfo();
		pass;

	def initWindowLayout(self):
		hbox = wx.BoxSizer(wx.HORIZONTAL);
		vbox = wx.BoxSizer(wx.VERTICAL);
		vbox.Add(self.title, 0, wx.ALIGN_CENTER|wx.TOP, 40);
		vbox.Add(self.reverifyButton, 0, wx.ALIGN_CENTER|wx.TOP, 40)
		vbox.Add(self.getCtr().getUIByKey("GaugeView"), 0, wx.ALIGN_CENTER);
		vbox.Add(self.detailTextCtrl, 0, wx.ALIGN_CENTER|wx.TOP, 10)
		vbox.Add(self.copyrightInfo, 0, wx.ALIGN_CENTER|wx.TOP, 4);
		hbox.Add(vbox, 0, wx.ALIGN_TOP|wx.LEFT|wx.RIGHT, 20);
		self.SetSizer(hbox);
		pass;

	def updateWindow(self, data):
		pass;

	def createTitle(self):
		self.title = wx.StaticText(self, label = AppConfig["WinTitle"], style = wx.ALIGN_CENTER);
		font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD);
		self.title.SetFont(font);

	def createReverifyButton(self):
		self.reverifyButton = wx.Button(self, label = u"重新校验", size = (-1, 32));
		self.reverifyButton.Bind(event = wx.EVT_BUTTON, handler = self.getCtr().onReverifyButton);
		wx.CallAfter(self.showReverifyButton, False);

	def createDetailTextCtrl(self):
		self.detailTextCtrl = wx.TextCtrl(self, value = "", size = (self.GetSize().x, 160), style = wx.TE_READONLY|wx.TE_MULTILINE);
		wx.CallAfter(self.showDetailTextCtrl, False);

	def createCopyrightInfo(self):
		self.copyrightInfo = wx.StaticText(self, label = AppConfig["Copyright"], style = wx.ALIGN_CENTER);

	def showReverifyButton(self, isShow = True):
		self.reverifyButton.Show(isShow);

	def showDetailTextCtrl(self, isShow = True, text = "", isReset = False):
		self.detailTextCtrl.Show(isShow);
		if isShow and text != "":
			if isReset:
				self.detailTextCtrl.SetValue(text);
			else:
				if self.detailTextCtrl.GetValue():
					text = "\n" + text;
				self.detailTextCtrl.AppendText(text);
		elif isReset:
			self.detailTextCtrl.SetValue("");
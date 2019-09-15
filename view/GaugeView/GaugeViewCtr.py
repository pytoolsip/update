# -*- coding: utf-8 -*-
# @Author: JimZhang
# @Date:   2018-12-08 13:41:18
# @Last Modified by:   JimDreamHeart
# @Last Modified time: 2019-03-16 13:46:27
import os;
import wx;

from event.Instance import *; # local
from utils.baseUtil import *; # local

from view.GaugeView.GaugeViewUI import *;

class GaugeViewCtr(object):
	"""docstring for GaugeViewCtr"""
	def __init__(self, parent, params = {}):
		super(GaugeViewCtr, self).__init__();
		self._className_ = GaugeViewCtr.__name__;
		self._curPath = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/";
		self.__CtrMap = {}; # 所创建的控制器
		self.initUI(parent, params); # 初始化视图UI
		self.registerEventMap(); # 注册事件

	def __del__(self):
		self.__dest__();

	def __dest__(self):
		if not hasattr(self, "_unloaded_"):
			self._unloaded_ = True;
			self.__unload__();

	def __unload__(self):
		self.unregisterEventMap(); # 注销事件
		self.delCtrMap(); # 銷毀控制器列表

	def getRegisterEventMap(self):
		return {
		};

	def delCtrMap(self):
		for key in self.__CtrMap:
			DelCtr(self.__CtrMap[key]);
		self.__CtrMap.clear();

	def initUI(self, parent, params):
		# 创建视图UI类
		self.__ui = GaugeViewUI(parent, curPath = self._curPath, viewCtr = self, params = params);
		self.__ui.initView();

	def getUI(self):
		return self.__ui;

	"""
		key : 索引所创建控制类的key值
		path : 所创建控制类的路径
		parent : 所创建控制类的UI的父节点，默认为本UI
		params : 扩展参数
	"""
	def createCtrByKey(self, key, parent = None, params = {}):
		viewCtr = None;
		if not parent:
			parent = self.getUI();
		if viewCtr:
			self.__CtrMap[key] = viewCtr;

	def getCtrByKey(self, key):
		return self.__CtrMap.get(key, None);

	def getUIByKey(self, key):
		ctr = self.getCtrByKey(key);
		if ctr:
			return ctr.getUI();
		return None;
		
	def registerEventMap(self):
		eventMap = self.getRegisterEventMap();
		for eventId, callbackName in eventMap.items():
			EventSystem.register(eventId, self, callbackName);

	def unregisterEventMap(self):
		eventMap = self.getRegisterEventMap();
		for eventId, callbackName in eventMap.items():
			EventSystem.unregister(eventId, self, callbackName);

	def updateView(self, data):
		self.__ui.updateView(data);
		
	def getGaugeValue(self):
		self.__ui.getGaugeValue();
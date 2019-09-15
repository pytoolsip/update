# -*- coding: utf-8 -*-
# @Author: JimZhang
# @Date:   2018-10-09 22:41:23
# @Last Modified by:   JimDreamHeart
# @Last Modified time: 2019-03-16 13:46:28

import wx;
import threading;
import copy;

from event.Instance import *; # local
from config.AppConfig import *; # local
from utils.baseUtil import *; # local

from window.MainWindow.MainWindowUI import *; # local

from view.GaugeView.GaugeViewCtr import *; # local

class MainWindowCtr(object):
	"""docstring for MainWindowCtr"""
	def __init__(self, parent = None, params = {}):
		super(MainWindowCtr, self).__init__();
		self._className_ = MainWindowCtr.__name__;
		self._curPath = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") + "/";
		self.__CtrMap = {}; # 所创建的控制器
		self.initUI(parent);
		self.registerEventMap(); # 注册事件
		self.__scheduleTaskList = []; # 调度任务列表

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
			EventID.ADD_SCHEDULE_TASK : "addScheduleTask",
			EventID.START_SCHEDULE_TASK : "startScheduleTask",
			EventID.CLEAR_SCHEDULE_TASK : "clearScheduleTask",
		};

	def delCtrMap(self):
		for key in self.__CtrMap:
			DelCtr(self.__CtrMap[key]);
		self.__CtrMap.clear();

	def initUI(self, parent = None):
		# 创建视图UI类
		windowTitle = AppConfig["Title"];
		windowSize = AppConfig["Size"];
		windowStyle = wx.DEFAULT_FRAME_STYLE^(wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX|wx.RESIZE_BORDER|wx.SYSTEM_MENU);
		self.__ui = MainWindowUI(parent, id = -1, title = windowTitle, size = windowSize, style = windowStyle, curPath = self._curPath, windowCtr = self);
		self.__ui.SetBackgroundColour(wx.Colour(250,250,250));
		self.__ui.initWindow();

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
		# 根据key值创建ViewCtr
		if key == "GaugeView":
			viewCtr = GaugeViewCtr(parent, params);
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
			
	def updateWindow(self, data):
		self.__ui.updateWindow(data);

	# 重新校验按钮回调
	def onReverifyButton(self, event = None):
		self.getUI().showReverifyButton(isShow = False);
		self.getUI().showDetailTextCtrl(isShow = False, isReset = True);
		self.handleScheduleEvent();

	def addScheduleTask(self, data):
		if callable(data.get("scheduleTask")):
			# 添加到任务列表
			self.__scheduleTaskList.append({
				"task" : data["scheduleTask"],
				"text" : data.get("text", "正在更新"),
				"args" : data.get("args", {}),
				"failInfo" : data.get("failInfo", {}),
			});

	def handleScheduleEvent(self, callbackInfo = {}, failCallbackInfo = {}):
		# 保存回调函数信息
		if callable(callbackInfo.get("callback")):
			self.scheduleCallbackInfo = {
				"callback" : callbackInfo.get("callback"),
				"args": callbackInfo.get("args", {}),
				"failCallback" : failCallbackInfo.get("callback"),
				"failArgs" : failCallbackInfo.get("args", {}),
			};
		# 重置加载进度视图
		self.getCtrByKey("GaugeView").updateView({"isReset" : True});
		# 处理调度任务列表
		self.handleScheduleTaskList(copy.copy(self.__scheduleTaskList));

	def handleScheduleTaskList(self, scheduleTaskList = []):
		if len(scheduleTaskList) > 0:
			taskInfo = scheduleTaskList.pop(0);
			self.getCtrByKey("GaugeView").updateView({
				"text" : taskInfo["text"],
				"gauge" : 1 - (len(scheduleTaskList) + 1)/len(self.__scheduleTaskList),
			});
			# 启动线程
			threading.Thread(target = self.handleScheduleTask, args = (taskInfo, scheduleTaskList, )).start();
		else:
			self.getCtrByKey("GaugeView").updateView({
				"text" : "完成更新，开始运行平台程序。",
				"gauge" : 1,
			});
			if hasattr(self, "scheduleCallbackInfo"):
				self.scheduleCallbackInfo["callback"](*self.scheduleCallbackInfo["args"].get("list", []), **self.scheduleCallbackInfo["args"].get("dict", {}));

	def handleScheduleTask(self, taskInfo, scheduleTaskList = []):
		isContinue, taskResult = self.handleScheduleTaskInfo(taskInfo);
		if not isContinue:
			# 显示重新校验按钮
			wx.CallAfter(self.getUI().showReverifyButton);
			# 调用校验失败后的相关回调函数
			failInfo = taskInfo.get("failInfo", {});
			wx.CallAfter(self.getCtrByKey("GaugeView").updateView, {
				"text" : failInfo.get("text", "更新失败！"),
				"textColor" : failInfo.get("textColor", wx.Colour(255, 0, 0)),
			});
			failCallback = None;
			failArgs = {};
			if isinstance(taskResult, tuple) and len(taskResult) > 0:
				failCallback = taskResult[0];
				if len(taskResult) > 1:
					failArgs["list"] = taskResult[1:];
			if not callable(failCallback) and callable(failInfo.get("failCallback")):
				failCallback = failInfo.get("failCallback");
				failArgs = failInfo.get("failArgs", {});
			if callable(failCallback):
				def failCallbackFunc():
					if failCallback(*failArgs.get("list", []), **failArgs.get("dict", {})):
						self.getCtrByKey("GaugeView").updateView({"textColor" : wx.Colour(0, 0, 0)})
						# 继续执行任务列表中的任务
						scheduleTaskList.insert(0, taskInfo);
						self.handleScheduleTaskList(scheduleTaskList);
				wx.CallAfter(failCallbackFunc);
			else:
				# 调用校验失败后的回调函数
				if hasattr(self, "scheduleCallbackInfo") and callable(self.scheduleCallbackInfo.get("failCallback")):
					failArgs = self.scheduleCallbackInfo.get("failArgs", {});
					wx.CallAfter(self.scheduleCallbackInfo.get("failCallback"), *failArgs.get("list", []), **failArgs.get("dict", {}));
			return; # 不执行以下逻辑
		# 继续执行任务列表中的任务
		wx.CallAfter(self.handleScheduleTaskList, scheduleTaskList);

	def handleScheduleTaskInfo(self, taskInfo = {}):
		isContinue, taskResult = True, None;
		if callable(taskInfo.get("task")):
			args = taskInfo.get("args", {});
			def callback(rate):
				wx.CallAfter(self.addSingleGaugeValue, rate);
			result = taskInfo.get("task")(*args.get("list", []), **args.get("dict", {}), callback = callback);
			if isinstance(result, tuple) and len(result) > 0:
				isContinue = result[0];
				if len(result) > 1:
					taskResult = result[1:];
			else:
				isContinue = result;
		return isContinue, taskResult;

	# 开始任务
	def startScheduleTask(self, data):
		self.handleScheduleEvent(self, data.get("callbackInfo", {}), data.get("failCallbackInfo", {}));

	# 清除任务
	def clearScheduleTask(self, data = None):
		self.__scheduleTaskList =[];

	def addSingleGaugeValue(self, rate):
		curVal = self.getCtrByKey("GaugeView").getGaugeValue();
		self.getCtrByKey("GaugeView").updateView({
			"gauge" : curVal + rate / len(self.__scheduleTaskList),
		});
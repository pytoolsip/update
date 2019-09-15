import sys;
import wx
import time;
import os;
import base64;
import shutil;
import zipfile;
from enum import Enum, unique;
global CUR_EVENT_ID;
CUR_EVENT_ID = -1;
def getNewEventId():
	global CUR_EVENT_ID;
	CUR_EVENT_ID += 1;
	return CUR_EVENT_ID;
@unique
class EVENT_ID(Enum):
	# 获取新的事件ID【供具体工具创建新的事件ID】
	@staticmethod
	def getNewId():
		return getNewEventId();
	EXIT_APP = getNewEventId(); # 关闭窗口事件
	DO_QUIT_APP = getNewEventId(); # 主动退出窗口事件
	ADD_SCHEDULE_TASK = getNewEventId(); # 添加任务
	START_SCHEDULE_TASK = getNewEventId(); # 开始任务
	CLEAR_SCHEDULE_TASK = getNewEventId(); # 清除任务
@unique
class EventState(Enum):
	NormalState = 0;
	UnRegisterState = 1;
class EventDispatcher(object):
	"""docstring for EventDispatcher"""
	def __init__(self):
		super(EventDispatcher, self).__init__();
		self.__dispatchDepth = 0;
		self.__registerIds = [];
		self.__listeners = [];
		self.initByEventIds();
	def initByEventIds(self):
		# 事件Id是从0开始自增，故而range函数的参数为当前事件Id值加1
		for i in range(CUR_EVENT_ID + 1):
			self.__registerIds.append({});
			self.__listeners.append([]);
	def updateEventIds(self):
		eventCount = max(len(self.__registerIds), len(self.__listeners));
		if CUR_EVENT_ID + 1 > eventCount:
			for i in range(eventCount, CUR_EVENT_ID + 1):
				self.__registerIds.append({});
				self.__listeners.append([]);
	def checkIsExistRegisterId(self, eventId, targetObj, callbackName):
		registerIdsDict = self.__registerIds[eventId];
		targetObjId = id(targetObj);
		if (targetObjId in registerIdsDict) and (callbackName in registerIdsDict[targetObjId]):
			return True;
		return False;
	def addRegisterId(self, eventId, targetObj, callbackName):
		registerIdsDict = self.__registerIds[eventId];
		targetObjId = id(targetObj);
		if targetObjId in registerIdsDict:
			registerIdsDict[targetObjId].append(callbackName);
		else:
			registerIdsDict[targetObjId] = [callbackName];
		pass;
	def removeRegisterId(self, eventId, targetObjId, callbackId):
		registerIdsDict = self.__registerIds[eventId];
		registerIdsDict[targetObjId].pop(callbackId);
	def register(self, event, targetObj, callbackName):
		try:
			eventId = event.value;
			if not self.checkIsExistRegisterId(eventId, targetObj, callbackName):
				self.__listeners[eventId].append({"target" : targetObj, "callbackName" : callbackName, "state" : EventState.NormalState});
				self.addRegisterId(eventId, targetObj, callbackName);
			else:
				raise Exception("Can\'t register the event(\"{0}\") repeatedly!".format(event));
		except Exception:
			raise Exception("Can\'t register the event(\"{0}\") !".format(event));
	def unregister(self, event, targetObj, callbackName):
		eventId = event.value;
		targetObjId = id(targetObj);
		listeners = self.__listeners[eventId];
		for i in range(len(listeners)-1, 0 ,-1):
			listener = listeners[i];
			if targetObjId == id(listener["target"]) and callbackName == listener["callbackName"]:
				listener["state"] = EventState.UnRegisterState;
				if self.__dispatchDepth == 0:
					self.removeRegisterId(eventId, targetObjId, callbackId);
					listeners.pop(i);
	def unregisterByTaget(self, event, targetObj):
		eventId = event.value;
		targetObjId = id(targetObj);
		listeners = self.__listeners[eventId];
		for i in range(len(listeners)-1, 0 ,-1):
			listener = listeners[i];
			if targetObjId == id(listener["target"]):
				listener["state"] = EventState.UnRegisterState;
				if self.__dispatchDepth == 0:
					listeners.pop(i);
	def dispatch(self, event, data, callObj = None):
		try:
			self.__dispatchDepth += 1;
			eventId = event.value;
			listeners = self.__listeners[eventId];
			if len(listeners) == 0:
				return;
			for listener in listeners:
				if listener["state"] == EventState.NormalState:
					targetObj = listener["target"];
					# 判断并初始化targetObj的EventIdListByDispatched_属性
					if not hasattr(targetObj, "_EventKeyListByDispatched_"):
						targetObj._EventKeyListByDispatched_ = [];
					# 判断eventKey是否在targetObj.EventIdListByDispatched_中
					eventKey = str(eventId) + listener["callbackName"];
					if eventKey not in targetObj._EventKeyListByDispatched_:
						targetObj._EventKeyListByDispatched_.append(eventKey);
						# 执行所注册事件的方法
						getattr(targetObj, listener["callbackName"])(data);
						# 移除targetObj的EventKeyListByDispatched_属性
						targetObj._EventKeyListByDispatched_.remove(eventKey);
					else:
						raise Exception("It calls the function(\"{0}\") of object(id:\"{1}\") in recursion !".format(listener["callbackName"], id(targetObj)));
			self.__dispatchDepth -= 1;
			pass;
		except Exception as e:
			raise Exception("It doesn\'t dispatch the event(\"{0}\")! [{1}] .".format(eventId, e));

EventSystem = EventDispatcher();
EventID = EVENT_ID;
AppConfig = {
	"Title" : u"PyToolsIP Update",
	"Size" : (640, 420),
	"Copyright" : u"Copyright(C) 2018-2019 JimDreamHeart. All Rights Reserved",
	"WinTitle" : u"更新 PyToolsIP【Python工具集成平台】",
	"ContentColor" : "#CDCDCD",
	"homeUrl" : "http://jimdreamheart.club",
	# "homeUrl" : "http://localhost:8000",
	"reqInfoUrl" : "http://jimdreamheart.club/pytoolsip/reqinfo",
	# "reqInfoUrl" : "http://localhost:8000/reqinfo",
};
PngConfig = {
	"AppIcon": "AAABAAEAQEAAAAEAIAAoQgAAFgAAACgAAABAAAAAgAAAAAEAIAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8JCQn/Jycn/zY2Nv8tLS3/BQUF/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9ERET/qqqq/5OTk/87Ozv/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/FRUV/25ubv/AwMD/+/v7/////////////////+3t7f+Pj4//Dw8P/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP87Ozv/+fn5/////////////v7+/7Gxsf8gICD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8aGhr/k5OT//X19f///////////////////////////////////////////9jY2P8dHR3/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/mZmZ////////////////////////////7e3t/0pKSv0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wkJCf98fHz99fX1////////////////////////////////////////////////////////////ycnJ/QICAv8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/7Ozs//////////////////////////////////9/f3/enp6/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/0ZGRv/f39////////////////////////////////////////////////////////////////////////////9lZWX/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP+jo6P///////////////////////////////////////////+ZmZn/AgIC/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/CgoK/5SUlP39/f3/////////////////////////////////////////////////////////////////////////////////2NjY/QAAAP8AAAD/AAAA/wkJCf8GBgb/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/e3t7/////////////////////////////////////////////////6mpqf8EBAT/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Kysr/9fX1/3///////////////////////////////////////////////////////////////////////////////////////////7+/v8nJyf9AAAA/wAAAP8AAAD/ExMT/yUlJf8YGBj/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/0BAQP//////////////////////////////////////////////////////rKys/QUFBf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/V1dX/fT09P/19fX/0tLS/7a2tv+mpqb/mZmZ/6ioqP+3t7f/0NDQ//Dw8P//////////////////////////////////////////////////////YmJi/QAAAP8AAAD/AAAA/wAAAP8AAAD/EhIS/y4uLv8ZGRn9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8EBAT/7e3t/f////////////////////////////////////////////////////+srKz9BgYG/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8CAgL/W1tb/XV1df8tLS3/AwMD/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8CAgL/MjIy/3d3d//U1NT//////////////////////////////////////4uLi/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/FBQU/zc3N/0WFhb/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/5ycnP3//////////////////////////////////////////////////////////6ioqP8CAgL/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AwMD/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AQEB/0hISP/X19f///////////////////////////+jo6P/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Jycn/z09Pf0NDQ3/AAAA/wAAAP8AAAD/AAAA/wAAAP8tLS3//f39//////////////////////+JiYn9LS0t/1xcXP/Dw8P//v7+////////////l5eX/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/BQUF/5KSkv3+/v7/////////////////oaGh/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/QUFB/UVFRf8AAAD/AAAA/wAAAP8AAAD/AAAA/6+vr/3////////////////u7u79BgYG/wAAAP8AAAD/AAAA/0ZGRv/W1tb///////7+/v98fHz9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/lJSU/////////////////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8UFBT/WVlZ/SIiIv8AAAD/AAAA/wAAAP80NDT9/v7+////////////wcHB/wAAAP8AAAD/AAAA/wAAAP8AAAD/BgYG/39/f//5+fn//v7+/2FhYf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wUFBf/X19f9//////////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9ERET9ZmZm/wcHB/8AAAD/AAAA/62trf///////////7u7u/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/KSkp/8nJyf37+/v/R0dH/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/WVlZ////////////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xUVFf+NjY3/PT09/QAAAP8eHh798/Pz/f////+7u7v/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8DAwP/c3Nz/+np6f8sLCz/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wUFBf/y8vL9/////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/3Jycv2Pj4//DAwM/319ff3/////wsLC/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8oKCj/rKys/RgYGP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/xsbG/f////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/OTk5/cbGxv9OTk79xsbG/dfX1/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wYGBv9eXl79Dg4O/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/6CgoP3/////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8ZGRn/zMzM/cjIyP3s7Oz9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wICAv8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP+goKD9/////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wkJCf+srKz9+/v7/0RERP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/qqqq/f////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AQEB/4eHh/3+/v7/kpKS/QgICP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/9DQ0P3/////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/6enp/f/////Y2Nj/Nzc3/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/w8PD//6+vr//////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/9bW1v28vLz9+fn5//v7+/98fHz9AwMD/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9jY2P///////////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP+/v7/939/f/VNTU/35+fn//////8nJyf8fHx//AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8DAwP/2NjY/f//////////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/oqKi/f////9iYmL/UVFR//j4+P//////7e3t/1hYWP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/e3t7/f///////////////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/46Ojv//////2tra/QEBAf9VVVX9+fn5///////+/v7/mZmZ/QgICP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/VFRU/fz8/P////////////////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9+fn7///////////9LS0v9AAAA/2hoaP3+/v7////////////S0tL/JSUl/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/aGho//v7+///////////////////////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/a2tr////////////u7u7/wAAAP8AAAD/gICA//////////////////Dw8P9SUlL9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8jIyP/t7e3/////////////////////////////////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/1hYWP////////////z8/P8gICD9AAAA/wAAAP+jo6P9/////////////////v7+/46Ojv8DAwP/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AwMD/0BAQP+np6f/+fn5//////////////////////////////////////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9PT0//////////////////goKC/QAAAP8AAAD/CQkJ/83Nzf3/////////////////////vb29/xUVFf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/CAgI/zIyMv9kZGT/oKCg/+rq6v//////////////////////////////////////////////////////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/QUFB/////////////////9zc3P0AAAD/AAAA/wAAAP8iIiL98PDw///////////////////////e3t7/Nzc3/ykpKf8oKCj/Ly8v/zw8PP9gYGD/j4+P/7q6uv/T09P/7e3t/////////////////////////////////////////////////////////////////////////////////5OTk/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/z8/P///////////////////////Ozs7/wAAAP8AAAD/AAAA/1dXV/3///////////////////////////f39/9cXFz/AAAA/wAAAP8AAAD/AAAA/wAAAP8WFhb/Tk5O/4mJif/Q0ND//v7+//////////////////////////////////////////////////////////////////////+SkpL/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8xMTH//////////////////////5WVlf0AAAD/AAAA/wAAAP8AAAD/ra2t/f///////////////////////////v7+/4SEhP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/x8fH/9/f3//5OTk////////////////////////////////////////////////////////////kpKS/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/ODg4///////////////////////l5eX9AQEB/wAAAP8AAAD/AAAA/xYWFv/u7u79///////////////////////////+/v7/oaGh/QQEBP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wUFBf9aWlr/1NTU/////////////////////////////////////////////////5KSkv8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/0BAQP///////////////////////////y4uLv0AAAD/AAAA/wAAAP8AAAD/cHBw/f////////////////////////////////////+urq7/BwcH/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wMDA/9kZGT/4+Pj//////////////////////////////////////+SkpL/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9JSUn///////////////////////////96enr/AAAA/wAAAP8AAAD/AAAA/wQEBP/d3d3//////////////////////////////////////76+vv8PDw//AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xMTE/+srKz/////////////////////////////////kpKS/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/YGBg////////////////////////////wcHB/wAAAP8AAAD/AAAA/wAAAP8AAAD/b29v/f//////////////////////////////////////////ysrK/Q8PD/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/2VlZf/39/f//////////////////////4mJif0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/35+fv////////////////////////////f39/8GBgb/AAAA/wAAAP8AAAD/AAAA/wwMDP3w8PD////////////////////////////////////////////Dw8P/DAwM/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/RUVF/fT09P////////////////+Dg4P9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP+ysrL9////////////////////////////////Nzc3/QAAAP8AAAD/AAAA/wAAAP8AAAD/oaGh/////////////////////////////////////////////////7Kysv8DAwP/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP85OTn98/Pz////////////g4OD/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8PDw/99PT0/f///////////////////////////////2pqav0AAAD/AAAA/wAAAP8AAAD/AAAA/1FRUf//////////////////////////////////////////////////////j4+P/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/0tLS//9/f3//////4ODg/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/hISE/f////////////////////////////////////+Tk5P9AAAA/wAAAP8AAAD/AAAA/wAAAP8RERH9/f39//////////////////////////////////////////////////7+/v9WVlb/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/hISE/f////+AgID9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wkJCf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/SkpK/fv7+///////////////////////////////////////t7e3/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/+Hh4f3/////////////////////////////////////////////////////7+/v/RoaGv0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wMDA//Q0ND/dHR0/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8EBAT/RUVF/WhoaP8jIyP/AAAA/wAAAP8AAAD/AAAA/wAAAP8YGBj/g4OD//n5+f///////////////////////////////////////////9nZ2f8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP/BwcH9//////////////////////////////////////////////////////////+np6f/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Q0ND/XR0dP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8aGhr/n5+f/+fn5//Dw8P/rq6u/7CwsP/S0tL/+vr6///////////////////////////////////////////////////////q6ur/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/tra2/f///////////////////////////////////////////////////////////v7+/zMzM/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wICAv9paWn7AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8tLS3/r6+v//7+/v//////////////////////////////////////////////////////////////////////6urq/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/8XFxf3///////////////////////////////////////////////////////////////+fn5/9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9YWFj9cnJy/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP87Ozv/u7u7//7+/v///////////////////////////////////////////////////////////+Tk5P8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP/k5OT9////////////////////////////////////////////////////////////////8fHx/wgICP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8gICD/7e3t/2ZmZv0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP88PDz/qamp//r6+v/////////////////////////////////////////////////ExMT9AAAA/wAAAP8AAAD/AAAA/wAAAP8kJCT9/v7+//////////////////////////////////////////////////////////////////////89PT3/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8QEBD/0tLS/f////9mZmb9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8iIiL/iIiI/+jo6P//////////////////////////////////////gICA/QAAAP8AAAD/AAAA/wAAAP8AAAD/gICA////////////////////////////////////////////////////////////////////////////ZmZm/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8ZGRn90dHR////////////WVlZ/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8JCQn/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8GBgb/SUlJ/5mZmf/W1tb//Pz8////////////ycnJ/w8PD/8AAAD/AAAA/wAAAP8AAAD/FhYW/e3t7f///////////////////////////////////////////////////////////////////////////3Z2dv0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9GRkb95ubm/////////////////1dXV/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/CgoK/0NDQ/0VFRX/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wcHB/8fHx//HBwc/wAAAP8AAAD/AAAA/wAAAP8AAAD/BgYG/7m5uf3///////////////////////////////////////////////////////////////////////////////9ubm79AAAA/wAAAP8AAAD/AAAA/zo6Ov+0tLT//v7+//////////////////////9LS0v9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Tk5O/21tbf0ODg7/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/BwcH/6+vr/3/////////////////////////////////////////////////////////////////////////////////////S0tL/QAAAP8AAAD/AAAA/3d3d/39/f3/////////////////////////////////SUlJ/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8eHh7/paWl/YCAgP8UFBT/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Hx8f/8jIyP//////////////////////////////////////////////////////////////////////////////////////8/Pz/wsLC/8AAAD/AAAA/ywsLP/+/v7//////////////////////////////////////zMzM/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9VVVX/29vb/6ioqP9JSUn/AwMD/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8KCgr/eXl5/fHx8f///////////////////////////////////////////////////////////////////////////////////////////5KSkv0AAAD/AAAA/wAAAP9JSUn9//////////////////////////////////////z8/P8NDQ39AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wsLC/+CgoL99/f3/+vr6/+ioqL/WVlZ/x8fH/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/BQUF/zo6Ov+Ghob/6urq/////////////////////////////////////////////////////////////////////////////////////////////////+Li4v8SEhL9AAAA/wAAAP8AAAD/bGxs/f/////////////////////////////////////Jycn9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xwcHP+ampr/+vr6////////////7+/v/83Nzf+srKz/pqam/6ampv+rq6v/z8/P//j4+P///////////////////////////////////////////////////////////////////////////////////////////////////////////+7u7v8uLi7/AAAA/wAAAP8AAAD/AAAA/7W1tf3/////////////////////////////////////XV1d/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/yIiIv+YmJj/9vb2/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////93d3f8wMDD/AAAA/wAAAP8AAAD/AAAA/yQkJP/6+vr/////////////////////////////////ycnJ/QMDA/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xQUFP99fX3/5eXl////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////+/v7/4+Pj/8NDQ3/AAAA/wAAAP8AAAD/AAAA/wICAv+9vb3/////////////////////////////////4uLi/yAgIP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wQEBP9HR0f/oKCg//Dw8P/////////////////////////////////////////////////////////////////////////////////////////////////6+vr/oaGh/zAwMP8AAAD/AAAA/wAAAP8AAAD/AAAA/wQEBP+fn5/9////////////////////////////////yMjI/xwcHP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8HBwf/RERE/4eHh//Kysr/+vr6////////////////////////////////////////////////////////////9PT0/7e3t/9nZ2f/FRUV/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/x8fH/+8vLz9///////////////////////////i4uL/aWlp/wMDA/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wkJCf83Nzf/ZWVl/4mJif+dnZ3/rKys/62trf+srKz/nZ2d/4aGhv9hYWH/ODg4/wYGBv8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/IyMj/4mJif/19fX///////39/f/o6Oj/w8PD/4eHh/9DQ0P/AwMD/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xYWFv8lJSX/Jycn/x8fH/8LCwv/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
};
from urllib import request
import json
def requestJson(data):
    kv = [];
    for k,v in data.items():
        kv.append(f"{k}={v}");
    url = AppConfig["reqInfoUrl"];
    try:
        resp = request.urlopen(f"{url}?"+"&".join(kv));
        return True, json.loads(resp.read());
    except Exception as e:
        print(e);
    return False, None;
def _getJsonData_(filePath):
	if os.path.exists(filePath):
		with open(filePath, "r") as f:
			return json.loads(f.read());
	return {};
def _getMd5Map_(tempPath, targetPath):
	tmpMd5, targetMd5 = {}, {};
	fileName = "_file_md5_map_.json";
	filePath = os.path.join(tempPath, fileName);
	if os.path.exists(filePath):
		tmpMd5 = _getJsonData_(filePath);
	filePath = os.path.join(targetPath, fileName);
	if os.path.exists(filePath):
		targetMd5 = _getJsonData_(filePath);
	return tmpMd5, targetMd5;
def _copyFileByMd5s_(tempPath, targetPath):
	tmpMd5Map, tgMd5Map = _getMd5Map_(tempPath, targetPath);
	for k,v in tmpMd5Map.items():
		tmpFile, tgFile = os.path.join(tempPath, k), os.path.join(targetPath, k);
		if os.path.exists(tmpFile) and v == tgMd5Map.get(k, ""):
			continue; # 已存在且md5值一样，则跳过
		if not os.path.exists(tgFile):
			return False; # 不存在目标文件，则更新失败
		shutil.copyfile(tgFile, tmpFile); # 拷贝文件
	return True;
def _getDependMods_(assetsPath):
	modList, modFile = [], os.path.join(assetsPath, "depends.mod");
	if not os.path.exists(modFile):
		return modList;
	with open(modFile, "r") as f:
		for line in f.readlines():
			mod = line.strip();
			if mod not in modList:
				modList.append(mod);
	return modList;
def _diffDependMods_(tempPath, targetPath):
	modList = [];
	tempModList, tgtModList = _getDependMods_(tempPath), _getDependMods_(targetPath);
	for mod in tempModList:
		if mod not in tgtModList:
			modList.append(mod);
	return modList;
def _checkDependMapJson_(tempPath, targetPath, dependMapFile):
	isChange, dependMap = False, _getJsonData_(dependMapFile);
	for mod in _diffDependMods_(tempPath, targetPath):
		if mod not in dependMap:
			dependMap[mod] = 1;
			isChange = True;
	if isChange:
		with open(dependMapFile, "w") as f:
			f.write(json.dumps(dependMap));
	return dependMap;
def verifyAssets(tempPath, targetPath, dependMapFile):
	if _copyFileByMd5s_(tempPath, targetPath):
		_checkDependMapJson_(tempPath, targetPath, dependMapFile); # 检测依赖模块配置
		return True;
	return False;
import threading;
import copy;
def DelCtr(ctr):
	Del(ctr.getUI());
	Del(ctr);
def Del(obj):
	if hasattr(obj, "__dest__"):
		obj.__dest__();
	del obj;
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
			fileName = f"temp_dzjh_{time.time()}.ico";
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
class GaugeViewUI(wx.Panel):
	"""docstring for GaugeViewUI"""
	def __init__(self, parent, id = -1, curPath = "", viewCtr = None, params = {}):
		self.initParams(params);
		super(GaugeViewUI, self).__init__(parent, id, pos = self.__params["pos"], size = self.__params["size"], style = self.__params["style"]);
		self._className_ = GaugeViewUI.__name__;
		self._curPath = curPath;
		self.__viewCtr = viewCtr;
	def initParams(self, params):
		# 初始化参数
		self.__params = {
			"pos" : (0,0),
			"size" : (-1,-1),
			"style" : wx.BORDER_NONE,
			"fgColour" : wx.Colour(0,0,0),
			"label" : "正在加载...",
		};
		for k,v in params.items():
			self.__params[k] = v;
	def getCtr(self):
		return self.__viewCtr;
	def initView(self):
		self.createControls(); # 创建控件
		self.initViewLayout(); # 初始化布局
	def createControls(self):
		# self.getCtr().createCtrByKey("key"); # , parent = self, params = {}
		self.createGauge();
		self.createInfoText();
		pass;
	def initViewLayout(self):
		vbox = wx.BoxSizer(wx.VERTICAL);
		vbox.Add(self.text);
		vbox.Add(self.gauge, flag = wx.ALIGN_CENTER);
		self.SetSizer(vbox);
		pass;
	def updateView(self, data):
		if "text" in data:
			self.text.SetLabel(data["text"]);
		if "textColor" in data:
			self.text.SetForegroundColour(data["textColor"]);
		if "gauge" in data:
			self.gauge.SetValue(data["gauge"] * self.gauge.GetRange());
		if "isReset" in data:
			self.resetView(data);
	def createGauge(self):
		self.gauge = wx.Gauge(self, size = (self.GetSize()[0], 20), style = wx.GA_SMOOTH);
	def createInfoText(self):
		self.text = wx.StaticText(self, label = self.__params["label"], style = wx.ALIGN_LEFT);
	def resetView(self, data = {}):
		self.updateView({
			"text" : "",
			"textColor" : self.__params["fgColour"],
			"gauge" : 0,
		});
	def getGaugeValue(self):
		return self.gauge.GetValue() / self.gauge.GetRange();
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
		return self.__ui.getGaugeValue();
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
		self.__gaugeRecordVal = 0; # 进度记录值
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
			self.__gaugeRecordVal = 1 - (len(scheduleTaskList) + 1)/len(self.__scheduleTaskList);
			self.getCtrByKey("GaugeView").updateView({
				"text" : taskInfo["text"],
				"gauge" : self.__gaugeRecordVal,
			});
			# 启动线程
			threading.Thread(target = self.handleScheduleTask, args = (taskInfo, scheduleTaskList, )).start();
		else:
			self.__gaugeRecordVal = 1;
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
		self.handleScheduleEvent(data.get("callbackInfo", {}), data.get("failCallbackInfo", {}));
	# 清除任务
	def clearScheduleTask(self, data = None):
		self.__scheduleTaskList =[];
	def addSingleGaugeValue(self, rate):
		self.getCtrByKey("GaugeView").updateView({
			"gauge" : self.__gaugeRecordVal + rate / len(self.__scheduleTaskList),
		});
urlListName = "url_list.json"
def getUrlListPath(basePath):
    return os.path.join(basePath, "data", urlListName);
def getDependMapPath(basePath):
    return os.path.join(basePath, "data", "depend_map.json");
def checkPath(path):
    if not path:
        return "";
    path = path.replace("\\", "/");
    if path[0] == "/":
        return path[1:];
    return path;
class MainApp(wx.App):
    def __init__(self, version, projectPath, updatePath):
        super(MainApp, self).__init__();
        self.initParams(version, projectPath, updatePath);
        self.__isRunning = False;
        self.Bind(wx.EVT_QUERY_END_SESSION, self.onDestroy);
        self.registerEvent();
    def initParams(self, version, projectPath, updatePath):
        self.__version = version;
        self.__projectPath = projectPath;
        self.__updatePath = os.path.join(updatePath, "pytoolsip");
        self.__tempPath = os.path.join(updatePath, "temp_pytoolsip");
        self.__basePath = "";
        pass;
    def __del__(self):
        self.unregisterEvent();
    def registerEvent(self):
        EventSystem.register(EventID.DO_QUIT_APP, self, "onQuit");
    def unregisterEvent(self):
        EventSystem.unregister(EventID.DO_QUIT_APP, self, "onQuit");
    # 关闭窗口
    def onDestroy(self, event = None):
        if self.__isRunning and event:
            messageDialog = wx.MessageDialog(self.__mainWinCtr.getUI(), "正在下载更新中，是否确定要取消本次更新？", "取消更新", style = wx.YES_NO|wx.ICON_QUESTION);
            if messageDialog.ShowModal() == wx.ID_YES:
                if self.__tempPath and os.path.exists(self.__tempPath):
                    shutil.rmtree(self.__tempPath);
            elif event.CanVeto():
                    event.Veto();
        EventSystem.dispatch(EventID.EXIT_APP, {});
    # 退出窗口
    def onQuit(self, data = None):
        self.ExitMainLoop();
    # 创建主窗口
    def createWindows(self):
        self.__mainWinCtr = MainWindowCtr();
    # 执行程序
    def run(self):
        self.__isRunning = True;
        wx.CallLater(500, self.update); # 延迟500ms后运行平台程序
        self.MainLoop();
    # 执行更新逻辑
    def update(self):
        self.verifyPath();
        self.downloadIP();
    def onFinish(self):
        self.__isRunning = False;
        wx.CallLater(1000, self.runPytoolsip); # 延迟1s后运行平台程序
    def runPytoolsip(self):
        pjPath = os.path.abspath(self.__projectPath);
        if os.path.exists(pjPath):
            os.system(" ".join(["start /d", pjPath, "pytoolsip.exe"]));
        else:
            wx.MessageDialog(self.__mainWinCtr.getUI(), "未找到平台的运行程序！", "运行平台异常", style = wx.OK|wx.ICON_ERROR).ShowModal();
        self.onQuit();
    def verifyPath(self):
        if os.path.exists(getUrlListPath(self.__updatePath)):
            self.__basePath = self.__updatePath;
        elif os.path.exists(getUrlListPath(self.__projectPath)):
            self.__basePath = self.__projectPath;
        if not self.__basePath:
            self.onQuit();
            return;
        if os.path.exists(self.__tempPath):
            shutil.rmtree(self.__tempPath);
        os.makedirs(self.__tempPath);
    # 下载平台
    def downloadIP(self):
        ret, resp = requestJson({"key":"ptip", "req":"urlList", "version":self.__version});
        if ret:
            urlList = self.checkUrlList(resp.get("urlList", []));
            if len(urlList) > 0:
                self.saveUrlListResp(resp); # 保存请求数据
                self.createTasks(self.__tempPath, urlList); # 创建任务
                EventSystem.dispatch(EventID.START_SCHEDULE_TASK, {
                    "callbackInfo" : {"callback" : self.onFinish},
                });
            else:
                wx.MessageDialog(self.__mainWinCtr.getUI(), "下载平台失败！", "数据异常", style = wx.OK|wx.ICON_ERROR).ShowModal();
        else:
            wx.MessageDialog(self.__mainWinCtr.getUI(), "下载平台失败！", "网络异常", style = wx.OK|wx.ICON_ERROR).ShowModal();
    # 创建任务
    def createTasks(self, basePath, urlList):
        EventSystem.dispatch(EventID.CLEAR_SCHEDULE_TASK, {});
        for urlInfo in urlList:
            name, url = urlInfo.get("name", ""), urlInfo["url"];
            fileName = os.path.basename(url);
            _, ext = os.path.splitext(fileName);
            if name:
                filepath = os.path.join(basePath, checkPath(urlInfo["path"]), name+ext);
            else:
                filepath = os.path.join(basePath, checkPath(urlInfo["path"]), fileName);
            filepath = filepath.replace("\\", "/");
            # 添加下载任务
            url = AppConfig["homeUrl"] + url;
            EventSystem.dispatch(EventID.ADD_SCHEDULE_TASK, {
                "scheduleTask" : self.__download__,
                "text" : f"正在下载{url}",
                "args" : {
                    "list" : [url, filepath],
                },
                "failInfo" : {
                    "text" : f"下载{url}失败！",
                    # "failCallback" : self.showInstallModMsgDialog,
                },
            });
            # 判断是否zip文件
            if ext == ".zip":
                # 添加解压任务
                EventSystem.dispatch(EventID.ADD_SCHEDULE_TASK, {
                    "scheduleTask" : self.__unzip__,
                    "text" : f"正在解压{filepath}",
                    "args" : {
                        "list" : [filepath, os.path.join(basePath, checkPath(urlInfo["path"]))],
                    },
                    "failInfo" : {
                        "text" : f"解压{filepath}失败！",
                        # "failCallback" : self.showInstallModMsgDialog,
                    },
                });
        # 添加处理更新目录任务
        EventSystem.dispatch(EventID.ADD_SCHEDULE_TASK, {
            "scheduleTask" : self.__dealUpdatePath__,
            "text" : f"正在处理更新目录{self.__updatePath}",
            "failInfo" : {
                "text" : f"处理更新目录{self.__updatePath}失败！",
                # "failCallback" : self.showInstallModMsgDialog,
            },
        });
    # 保存url列表数据
    def saveUrlListResp(self, urlList):
        dataPath = os.path.join(self.__tempPath, "data"); # 数据路径
        if not os.path.exists(dataPath):
            os.makedirs(dataPath);
        with open(os.path.join(dataPath, urlListName), "w") as f:
            f.write(json.dumps(urlList));
            f.close();
    def getUrlKeyMap(self, urlList):
        keyMap = {};
        for urlInfo in urlList:
            keyMap["|".join([urlInfo.get("type", ""), urlInfo.get("name", "")])] = urlInfo;
        return keyMap;
    def checkUrlList(self, urlList):
        keyMap = self.getUrlKeyMap(urlList);
        baseKeyMap = {};
        urlListPath = getUrlListPath(self.__basePath);
        if os.path.exists(urlListPath):
            with open(urlListPath, "r") as f:
                baseJson = json.loads(f.read());
                baseKeyMap = self.getUrlKeyMap((baseJson.get("urlList", [])));
                f.close();
        # 返回检测结果
        retList = [];
        for k,v in keyMap.items():
            if k in baseKeyMap:
                for key in ["version", "key"]:
                    if key in v and v[key] != baseKeyMap[k].get(key, ""):
                        retList.append(v);
                        break;
            else:
                retList.append(v);
        return retList;
    # 校验文件路径
    def __checkFilePath__(self, filePath):
        dirPath = os.path.dirname(filePath);
        if not os.path.exists(dirPath):
            os.mkdir(dirPath);
    # 校验及处理更新目录
    def __dealUpdatePath__(self, callback = None):
        verifyAssets(self.__tempPath, self.__basePath, getDependMapPath(self.__projectPath));
        callback(0.5);
        if os.path.exists(self.__updatePath):
            shutil.rmtree(self.__updatePath);
        callback(0.75);
        shutil.move(self.__tempPath, self.__updatePath);
        return True;
    # 下载文件
    def __download__(self, url, filepath, callback = None):
        self.__checkFilePath__(filepath);
        def schedule(block, size, totalSize):
            callback(block*size/totalSize);
        request.urlretrieve(url, filepath, schedule);
        return True;
    # 解压文件
    def __unzip__(self, filepath, dirpath, isRmZip = True, callback = None):
        if not os.path.exists(filepath):
            return False;
        with zipfile.ZipFile(filepath, "r") as zf:
            totalCnt = len(zf.namelist());
            completeCnt = 0;
            for file in zf.namelist():
                zf.extract(file, dirpath);
                completeCnt += 1;
                callback(completeCnt/totalCnt);
            zf.close();
            # 移除zip文件
            if isRmZip:
                os.remove(filepath);
            return True;
        return False;

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        sys.exit(1);
    # 加载程序
    App = MainApp(*sys.argv[1:]);
    # 创建窗口
    App.createWindows();
    # 运行程序
    App.run();
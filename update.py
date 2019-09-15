import sys;
from tkinter import *
import time;
import os;
import base64;
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
	"WinTitle" : u"PyToolsIP【Python工具集成平台】",
	"ContentColor" : "#CDCDCD",
	"homeUrl" : "http://jimdreamheart.club",
	# "homeUrl" : "http://localhost:8000",
	"reqInfoUrl" : "http://jimdreamheart.club/pytoolsip/reqinfo",
	# "reqInfoUrl" : "http://localhost:8000/reqinfo",
};
PngConfig = {
	"AppIcon": "AAABAAEAQEAAAAEAIAAoQgAAFgAAACgAAABAAAAAgAAAAAEAIAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8JCQn/Jycn/zY2Nv8tLS3/BQUF/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9ERET/qqqq/5OTk/87Ozv/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/FRUV/25ubv/AwMD/+/v7/////////////////+3t7f+Pj4//Dw8P/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP87Ozv/+fn5/////////////v7+/7Gxsf8gICD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8aGhr/k5OT//X19f///////////////////////////////////////////9jY2P8dHR3/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/mZmZ////////////////////////////7e3t/0pKSv0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wkJCf98fHz99fX1////////////////////////////////////////////////////////////ycnJ/QICAv8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/7Ozs//////////////////////////////////9/f3/enp6/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/0ZGRv/f39////////////////////////////////////////////////////////////////////////////9lZWX/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP+jo6P///////////////////////////////////////////+ZmZn/AgIC/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/CgoK/5SUlP39/f3/////////////////////////////////////////////////////////////////////////////////2NjY/QAAAP8AAAD/AAAA/wkJCf8GBgb/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/e3t7/////////////////////////////////////////////////6mpqf8EBAT/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Kysr/9fX1/3///////////////////////////////////////////////////////////////////////////////////////////7+/v8nJyf9AAAA/wAAAP8AAAD/ExMT/yUlJf8YGBj/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/0BAQP//////////////////////////////////////////////////////rKys/QUFBf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/V1dX/fT09P/19fX/0tLS/7a2tv+mpqb/mZmZ/6ioqP+3t7f/0NDQ//Dw8P//////////////////////////////////////////////////////YmJi/QAAAP8AAAD/AAAA/wAAAP8AAAD/EhIS/y4uLv8ZGRn9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8EBAT/7e3t/f////////////////////////////////////////////////////+srKz9BgYG/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8CAgL/W1tb/XV1df8tLS3/AwMD/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8CAgL/MjIy/3d3d//U1NT//////////////////////////////////////4uLi/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/FBQU/zc3N/0WFhb/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/5ycnP3//////////////////////////////////////////////////////////6ioqP8CAgL/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AwMD/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AQEB/0hISP/X19f///////////////////////////+jo6P/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Jycn/z09Pf0NDQ3/AAAA/wAAAP8AAAD/AAAA/wAAAP8tLS3//f39//////////////////////+JiYn9LS0t/1xcXP/Dw8P//v7+////////////l5eX/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/BQUF/5KSkv3+/v7/////////////////oaGh/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/QUFB/UVFRf8AAAD/AAAA/wAAAP8AAAD/AAAA/6+vr/3////////////////u7u79BgYG/wAAAP8AAAD/AAAA/0ZGRv/W1tb///////7+/v98fHz9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/lJSU/////////////////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8UFBT/WVlZ/SIiIv8AAAD/AAAA/wAAAP80NDT9/v7+////////////wcHB/wAAAP8AAAD/AAAA/wAAAP8AAAD/BgYG/39/f//5+fn//v7+/2FhYf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wUFBf/X19f9//////////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9ERET9ZmZm/wcHB/8AAAD/AAAA/62trf///////////7u7u/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/KSkp/8nJyf37+/v/R0dH/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/WVlZ////////////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xUVFf+NjY3/PT09/QAAAP8eHh798/Pz/f////+7u7v/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8DAwP/c3Nz/+np6f8sLCz/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wUFBf/y8vL9/////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/3Jycv2Pj4//DAwM/319ff3/////wsLC/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8oKCj/rKys/RgYGP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/xsbG/f////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/OTk5/cbGxv9OTk79xsbG/dfX1/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wYGBv9eXl79Dg4O/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/6CgoP3/////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8ZGRn/zMzM/cjIyP3s7Oz9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wICAv8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP+goKD9/////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wkJCf+srKz9+/v7/0RERP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/qqqq/f////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AQEB/4eHh/3+/v7/kpKS/QgICP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/9DQ0P3/////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/6enp/f/////Y2Nj/Nzc3/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/w8PD//6+vr//////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/9bW1v28vLz9+fn5//v7+/98fHz9AwMD/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9jY2P///////////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP+/v7/939/f/VNTU/35+fn//////8nJyf8fHx//AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8DAwP/2NjY/f//////////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/oqKi/f////9iYmL/UVFR//j4+P//////7e3t/1hYWP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/e3t7/f///////////////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/46Ojv//////2tra/QEBAf9VVVX9+fn5///////+/v7/mZmZ/QgICP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/VFRU/fz8/P////////////////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9+fn7///////////9LS0v9AAAA/2hoaP3+/v7////////////S0tL/JSUl/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/aGho//v7+///////////////////////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/a2tr////////////u7u7/wAAAP8AAAD/gICA//////////////////Dw8P9SUlL9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8jIyP/t7e3/////////////////////////////////6CgoP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/1hYWP////////////z8/P8gICD9AAAA/wAAAP+jo6P9/////////////////v7+/46Ojv8DAwP/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AwMD/0BAQP+np6f/+fn5//////////////////////////////////////+goKD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9PT0//////////////////goKC/QAAAP8AAAD/CQkJ/83Nzf3/////////////////////vb29/xUVFf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/CAgI/zIyMv9kZGT/oKCg/+rq6v//////////////////////////////////////////////////////oKCg/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/QUFB/////////////////9zc3P0AAAD/AAAA/wAAAP8iIiL98PDw///////////////////////e3t7/Nzc3/ykpKf8oKCj/Ly8v/zw8PP9gYGD/j4+P/7q6uv/T09P/7e3t/////////////////////////////////////////////////////////////////////////////////5OTk/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/z8/P///////////////////////Ozs7/wAAAP8AAAD/AAAA/1dXV/3///////////////////////////f39/9cXFz/AAAA/wAAAP8AAAD/AAAA/wAAAP8WFhb/Tk5O/4mJif/Q0ND//v7+//////////////////////////////////////////////////////////////////////+SkpL/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8xMTH//////////////////////5WVlf0AAAD/AAAA/wAAAP8AAAD/ra2t/f///////////////////////////v7+/4SEhP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/x8fH/9/f3//5OTk////////////////////////////////////////////////////////////kpKS/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/ODg4///////////////////////l5eX9AQEB/wAAAP8AAAD/AAAA/xYWFv/u7u79///////////////////////////+/v7/oaGh/QQEBP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wUFBf9aWlr/1NTU/////////////////////////////////////////////////5KSkv8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/0BAQP///////////////////////////y4uLv0AAAD/AAAA/wAAAP8AAAD/cHBw/f////////////////////////////////////+urq7/BwcH/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wMDA/9kZGT/4+Pj//////////////////////////////////////+SkpL/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9JSUn///////////////////////////96enr/AAAA/wAAAP8AAAD/AAAA/wQEBP/d3d3//////////////////////////////////////76+vv8PDw//AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xMTE/+srKz/////////////////////////////////kpKS/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/YGBg////////////////////////////wcHB/wAAAP8AAAD/AAAA/wAAAP8AAAD/b29v/f//////////////////////////////////////////ysrK/Q8PD/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/2VlZf/39/f//////////////////////4mJif0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/35+fv////////////////////////////f39/8GBgb/AAAA/wAAAP8AAAD/AAAA/wwMDP3w8PD////////////////////////////////////////////Dw8P/DAwM/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/RUVF/fT09P////////////////+Dg4P9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP+ysrL9////////////////////////////////Nzc3/QAAAP8AAAD/AAAA/wAAAP8AAAD/oaGh/////////////////////////////////////////////////7Kysv8DAwP/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP85OTn98/Pz////////////g4OD/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8PDw/99PT0/f///////////////////////////////2pqav0AAAD/AAAA/wAAAP8AAAD/AAAA/1FRUf//////////////////////////////////////////////////////j4+P/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/0tLS//9/f3//////4ODg/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/hISE/f////////////////////////////////////+Tk5P9AAAA/wAAAP8AAAD/AAAA/wAAAP8RERH9/f39//////////////////////////////////////////////////7+/v9WVlb/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/hISE/f////+AgID9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wkJCf8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/SkpK/fv7+///////////////////////////////////////t7e3/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/+Hh4f3/////////////////////////////////////////////////////7+/v/RoaGv0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wMDA//Q0ND/dHR0/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8EBAT/RUVF/WhoaP8jIyP/AAAA/wAAAP8AAAD/AAAA/wAAAP8YGBj/g4OD//n5+f///////////////////////////////////////////9nZ2f8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP/BwcH9//////////////////////////////////////////////////////////+np6f/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Q0ND/XR0dP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8aGhr/n5+f/+fn5//Dw8P/rq6u/7CwsP/S0tL/+vr6///////////////////////////////////////////////////////q6ur/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/tra2/f///////////////////////////////////////////////////////////v7+/zMzM/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wICAv9paWn7AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8tLS3/r6+v//7+/v//////////////////////////////////////////////////////////////////////6urq/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/8XFxf3///////////////////////////////////////////////////////////////+fn5/9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9YWFj9cnJy/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP87Ozv/u7u7//7+/v///////////////////////////////////////////////////////////+Tk5P8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP/k5OT9////////////////////////////////////////////////////////////////8fHx/wgICP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8gICD/7e3t/2ZmZv0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP88PDz/qamp//r6+v/////////////////////////////////////////////////ExMT9AAAA/wAAAP8AAAD/AAAA/wAAAP8kJCT9/v7+//////////////////////////////////////////////////////////////////////89PT3/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8QEBD/0tLS/f////9mZmb9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8iIiL/iIiI/+jo6P//////////////////////////////////////gICA/QAAAP8AAAD/AAAA/wAAAP8AAAD/gICA////////////////////////////////////////////////////////////////////////////ZmZm/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8ZGRn90dHR////////////WVlZ/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8JCQn/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8GBgb/SUlJ/5mZmf/W1tb//Pz8////////////ycnJ/w8PD/8AAAD/AAAA/wAAAP8AAAD/FhYW/e3t7f///////////////////////////////////////////////////////////////////////////3Z2dv0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9GRkb95ubm/////////////////1dXV/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/CgoK/0NDQ/0VFRX/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wcHB/8fHx//HBwc/wAAAP8AAAD/AAAA/wAAAP8AAAD/BgYG/7m5uf3///////////////////////////////////////////////////////////////////////////////9ubm79AAAA/wAAAP8AAAD/AAAA/zo6Ov+0tLT//v7+//////////////////////9LS0v9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Tk5O/21tbf0ODg7/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/BwcH/6+vr/3/////////////////////////////////////////////////////////////////////////////////////S0tL/QAAAP8AAAD/AAAA/3d3d/39/f3/////////////////////////////////SUlJ/QAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8eHh7/paWl/YCAgP8UFBT/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/Hx8f/8jIyP//////////////////////////////////////////////////////////////////////////////////////8/Pz/wsLC/8AAAD/AAAA/ywsLP/+/v7//////////////////////////////////////zMzM/0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP9VVVX/29vb/6ioqP9JSUn/AwMD/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8KCgr/eXl5/fHx8f///////////////////////////////////////////////////////////////////////////////////////////5KSkv0AAAD/AAAA/wAAAP9JSUn9//////////////////////////////////////z8/P8NDQ39AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wsLC/+CgoL99/f3/+vr6/+ioqL/WVlZ/x8fH/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/BQUF/zo6Ov+Ghob/6urq/////////////////////////////////////////////////////////////////////////////////////////////////+Li4v8SEhL9AAAA/wAAAP8AAAD/bGxs/f/////////////////////////////////////Jycn9AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xwcHP+ampr/+vr6////////////7+/v/83Nzf+srKz/pqam/6ampv+rq6v/z8/P//j4+P///////////////////////////////////////////////////////////////////////////////////////////////////////////+7u7v8uLi7/AAAA/wAAAP8AAAD/AAAA/7W1tf3/////////////////////////////////////XV1d/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/yIiIv+YmJj/9vb2/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////93d3f8wMDD/AAAA/wAAAP8AAAD/AAAA/yQkJP/6+vr/////////////////////////////////ycnJ/QMDA/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xQUFP99fX3/5eXl////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////+/v7/4+Pj/8NDQ3/AAAA/wAAAP8AAAD/AAAA/wICAv+9vb3/////////////////////////////////4uLi/yAgIP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wQEBP9HR0f/oKCg//Dw8P/////////////////////////////////////////////////////////////////////////////////////////////////6+vr/oaGh/zAwMP8AAAD/AAAA/wAAAP8AAAD/AAAA/wQEBP+fn5/9////////////////////////////////yMjI/xwcHP0AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8HBwf/RERE/4eHh//Kysr/+vr6////////////////////////////////////////////////////////////9PT0/7e3t/9nZ2f/FRUV/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/x8fH/+8vLz9///////////////////////////i4uL/aWlp/wMDA/8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wkJCf83Nzf/ZWVl/4mJif+dnZ3/rKys/62trf+srKz/nZ2d/4aGhv9hYWH/ODg4/wYGBv8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/IyMj/4mJif/19fX///////39/f/o6Oj/w8PD/4eHh/9DQ0P/AwMD/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/xYWFv8lJSX/Jycn/x8fH/8LCwv/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAA/wAAAP8AAAD/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
};
class MainApp(Tk):
    def __init__(self):
        super(MainApp, self).__init__();
        self.initTitle();
        self.initSize();
        self.initIcon();
        self.protocol("EXIT_APP", self.onDestroy);
        self.registerEvent();
    def __del__(self):
        self.unregisterEvent();
    def registerEvent(self):
        EventSystem.register(EventID.DO_QUIT_APP, self, "onQuit");
    def unregisterEvent(self):
        EventSystem.unregister(EventID.DO_QUIT_APP, self, "onQuit");
    # 设置标题
    def initTitle(self):
        self.title(AppConfig["Title"]);
    # 设置大小及位置
    def initSize(self):
        width, height = AppConfig["Size"];
        posX, posY = (self.winfo_screenwidth() - width) / 2, (self.winfo_screenheight() - height) / 2;
        self.geometry("%dx%d+%d+%d" % (width, height, posX, posY));
    # 初始化图标
    def initIcon(self):
        if "AppIcon" in PngConfig:
            img = base64.b64decode(PngConfig["AppIcon"].encode());
            fileName = f"temp_dzjh_{time.time()}.ico";
            with open(fileName, 'wb') as f:
                f.write(img);
            self.iconbitmap(fileName);
            os.remove(fileName);
    # 关闭窗口
    def onDestroy(self):
        EventSystem.dispatch(EventID.EXIT_APP, {});
        self.destroy();
    # 退出窗口
    def onQuit(self, data = None):
        # self.quit();
        self.destroy();
from tkinter import ttk;
from tkinter import messagebox;
import shutil;
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
import inspect;
import ctypes;
def stopThread(thread):
	try:
		if thread.isAlive():
			tid = ctypes.c_long(thread.ident);
			exctype = SystemExit;
			if not inspect.isclass(exctype):
				exctype = type(exctype);
			res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype));
			if res == 0:
				raise ValueError("Invalid thread !");
			elif res != 1:
				ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None);
				raise SystemError("PyThreadState_SetAsyncExc failed !");
	except Exception as e:
		print("stop thread failed !", e);

def _getJsonData_(filePath):
	if os.path.exists(filePath):
		with open(filePath, "r") as f:
			return json.loads(f.read());
	return {};
def _getMd5Map_(tempPath, targetPath):
	tmpMd5, targetMd5 = {}, {};
	fileName = "_file_md5_map_.json";
	filePath = os.path.join(tempPath, fileName);
	if os.path.exist(filePath):
		tmpMd5 = _getJsonData_(filePath);
	filePath = os.path.join(targetPath, fileName);
	if os.path.exist(filePath):
		targetMd5 = _getJsonData_(filePath);
	return tmpMd5, targetMd5;
def _copyFileByMd5s_(tempPath, targetPath):
	tmpMd5Map, tgMd5Map = _getMd5Map_(tempPath, targetPath);
	for k,v in tmpMd5Map.items():
		tmpFile, tgFile = os.path.join(tempPath, k), os.path.join(targetPath, k);
		if os.path.exist(tmpFile) and v == tgMd5Map.get(k, ""):
			continue; # 已存在且md5值一样，则跳过
		if not os.path.exist(tgFile):
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
from tkinter.filedialog import askdirectory;
import threading;
import zipfile;
def checkPath(path):
    if not path:
        return "";
    path = path.replace("\\", "/");
    if path[0] == "/":
        return path[1:];
    return path;
class DownloadUnZip(Frame):
    def __init__(self, parent):
        super(DownloadUnZip, self).__init__(parent, borderwidth = 1, relief = GROOVE, bg= AppConfig["ContentColor"]);
        self.__parent = parent;
        self.__taskList = [];
        self.__taskCnt = 0;
        self.pack(expand = YES, fill = BOTH);
        self.update();
        self.initView();
    def initView(self):
        Label(self, text="- 下载与解压 -", font=("宋体", 12), fg="gray", bg= AppConfig["ContentColor"]).pack(pady = (30, 20));
        # 初始化提示
        self.initTips();
        # 初始化进度条
        self.initProgressbar();
    def initTips(self):
        self.__tips = StringVar();
        Label(self, textvariable=self.__tips, font=("宋体", 10), bg= AppConfig["ContentColor"]).pack(padx = 10, pady = (40, 20));
    def initProgressbar(self):
        self.__progress = IntVar();
        ttk.Progressbar(self, length=int(self.__parent.winfo_width()), variable = self.__progress).pack(padx = 10, pady = (0, 100));
    def start(self, urlInfoList, basePath, onComplete = None):
        # print(f"Start download and unzip urlInfoList({urlInfoList}).");
        # 重置任务列表
        self.__taskList = [];
        for urlInfo in urlInfoList:
            name, url = urlInfo.get("name", ""), urlInfo["url"];
            fileName = os.path.basename(url);
            _, ext = os.path.splitext(fileName);
            if name:
                filepath = os.path.join(basePath, checkPath(urlInfo["path"]), name+ext);
            else:
                filepath = os.path.join(basePath, checkPath(urlInfo["path"]), fileName);
            filepath = filepath.replace("\\", "/");
            self.__taskList.append({"type" : "download", "url" : AppConfig["homeUrl"] + url, "filepath" : filepath});
            # 判断是否zip文件
            if ext == ".zip":
                self.__taskList.append({"type" : "unzip", "filepath" : filepath, "dirpath" : os.path.join(basePath, checkPath(urlInfo["path"]))});
        self.__taskCnt = len(self.__taskList); # 重置任务总数
        self.__onComplete = onComplete; # 重置完成任务列表的回调
        self.runTaskList(); # 运行任务
    def runTaskList(self):
        if len(self.__taskList) > 0:
            self.__progress.set((self.__taskCnt - len(self.__taskList))/self.__taskCnt * 100);
            task = self.__taskList.pop(0);
            if task["type"] == "download":
                self.__download__(task["url"], task["filepath"]);
            elif task["type"] == "unzip":
                self.__unzip__(task["filepath"], task["dirpath"]);
            # 执行下个任务
            self.runTaskList();
        else:
            self.__progress.set(100);
            if callable(self.__onComplete):
                self.__onComplete(); # 完成任务列表后回调
    # 获取上次的进度
    def getLastProgress(self):
        return (self.__taskCnt - len(self.__taskList))/self.__taskCnt * 100;
    # 校验文件路径
    def __checkFilePath__(self, filePath):
        dirPath = os.path.dirname(filePath);
        if not os.path.exists(dirPath):
            os.mkdir(dirPath);
    # 下载文件
    def __download__(self, url, filepath):
        self.__tips.set(f"正在下载：\n{url}");
        self.__checkFilePath__(filepath);
        request.urlretrieve(url, filepath, self._schedule_);
    # 下载回调
    def _schedule_(self, block, size, totalSize):
        rate = block*size / totalSize * 100;
        self.__progress.set(self.getLastProgress() + rate);
        tips = re.sub("\n\[\d+.?\d+\%\]", "", self.__tips.get());
        if block*size < totalSize:
            rate = round(rate, 2);
            self.__tips.set(f"{tips}\n[{rate}%]");
        else:
            url = tips.replace("正在下载：\n", "").strip();
            self.__tips.set(f"完成下载：\n{url}");
        pass;
    # 解压文件
    def __unzip__(self, filepath, dirpath, isRmZip = True):
        if not os.path.exists(filepath):
            return;
        self.__tips.set(f"开始解压：{filepath}");
        self._unzipFile_(filepath, dirpath, isRmZip);
    # 解压回调
    def _unzipFile_(self, filepath, dirpath, isRmZip = True):
        with zipfile.ZipFile(filepath, "r") as zf:
            totalCnt = len(zf.namelist());
            completeCnt = 0;
            for file in zf.namelist():
                self.__tips.set(f"正在解压：{file}");
                zf.extract(file, dirpath);
                completeCnt += 1;
                self.__progress.set(self.getLastProgress() + completeCnt/totalCnt * 100);
            zf.close();
            # 移除zip文件
            if isRmZip:
                self.__tips.set(f"正在移除文件：{filepath}");
                os.remove(filepath);
            self.__tips.set(f"完成解压：{filepath}");
urlListName = "url_list.json"
def getUrlListPath(basePath):
    return os.path.join(basePath, "data", urlListName);
def getDependMapPath(basePath):
    return os.path.join(basePath, "data", "depend_map.json");
class MainWindow(Frame):
    def __init__(self, parent, version, projectPath, updatePath):
        super(MainWindow, self).__init__(parent);
        self.__parent = parent;
        self.__version = version;
        self.__projectPath = projectPath;
        self.__updatePath = os.path.join(updatePath, "pytoolsip");
        self.__tempPath = os.path.join(updatePath, "temp_pytoolsip");
        self.__basePath = "";
        self.__thread = None;
        self.pack(expand = YES, fill = BOTH);
        self.initWindow();
        self.registerEvent();
        self.run();
    def __del__(self):
        self.stopThread();
        self.unregisterEvent();
    def onDestroy(self, data):
        if self.__thread: # 判断下载线程是否还存在
            if messagebox.askokcancel(title="取消更新", message="正在下载更新中，是否确定要取消本次更新？"):
                self.stopThread(); # 停止子线程
                # 移除更新路径内容
                if self.__tempPath and os.path.exists(self.__tempPath):
                    shutil.rmtree(self.__tempPath);
                    self.__tempPath = "";
    def registerEvent(self):
        EventSystem.register(EventID.EXIT_APP, self, "onDestroy");
    def unregisterEvent(self):
        EventSystem.unregister(EventID.EXIT_APP, self, "onDestroy");
    def stopThread(self):
        if self.__thread:
            stopThread(self.__thread);
            self.__thread = None;
    def initWindow(self):
        # 初始化标题
        Label(self, text=AppConfig["WinTitle"], font=("Arial", 20)).pack(pady = (40, 20));
        # 初始化版权信息
        Label(self, text=AppConfig["Copyright"], font=("宋体", 10)).pack(side = BOTTOM, pady = (20, 0));
        # 初始化内容
        self.initContent()
    def initContent(self):
        f = Frame(self, borderwidth = 2, relief = GROOVE, bg= AppConfig["ContentColor"]);
        f.pack(expand = YES, fill = BOTH);
        # 初始化下载进度条
        self.__du = DownloadUnZip(f);
        self.__du.forget();
        # 初始化提示信息
        self.__tipsVal = StringVar();
        self.__tips = Label(f, textvariable=self.__tipsVal, font=("宋体", 10), bg= AppConfig["ContentColor"]);
        self.__tips.pack(pady = (80, 10));
        # 初始化重新更新按钮
        self.__reUpdateBtn = Button(f, text="重新更新平台", command=self.reUpdate);
        self.__reUpdateBtn.forget();
        pass;
    # 开始更新平台
    def run(self):
        if os.path.exists(getUrlListPath(self.__updatePath)):
            self.__basePath = self.__updatePath;
        elif os.path.exists(getUrlListPath(self.__projectPath)):
            self.__basePath = self.__projectPath;
        if not self.__basePath:
            self.__tipsVal.set(f"更新平台【{self.__version}】失败！");
            EventSystem.dispatch(EventID.DO_QUIT_APP, {});
            return;
        if os.path.exists(self.__tempPath):
            shutil.rmtree(self.__tempPath);
        os.makedirs(self.__tempPath);
        self.downloadIPByThread(self.__version);
    # 启动新线程下载平台
    def downloadIPByThread(self, version):
        # print("downloadIP:", self.__tempPath, version);
        self.__tipsVal.set(f"准备开始下载平台【{version}】...");
        # 创建下载及解压视图
        self.__du.pack(expand = YES, fill = BOTH);
        # 停止之前的子线程
        self.stopThread();
        # 开始请求版本列表的新子线程
        self.__thread = threading.Thread(target = self.downloadIP, args = (version, ));
        self.__thread.setDaemon(True)
        self.__thread.start();
    # 下载平台
    def downloadIP(self, version):
        self.__tips.forget();
        ret, resp = requestJson({"key":"ptip", "req":"urlList", "version":version});
        if ret:
            urlList = self.checkUrlList(resp.get("urlList", []));
            if len(urlList) > 0:
                def onComplete():
                    self.__tips.pack(pady = (80, 10));
                    self.saveUrlListResp(resp);
                    self.verifyPath();
                    self.onComplete(version);
                self.__du.start(urlList, self.__tempPath, onComplete = onComplete);
            else:
                messagebox.showerror(title="数据异常", message="下载平台失败！");
                self.showFailedTips("平台数据异常，下载平台失败！");
        else:
            messagebox.showerror(title="网络异常", message="下载平台失败！");
            self.showFailedTips("网络连接异常，下载平台失败！");
        # 置空线程对象
        self.__thread = None;
    # 保存url列表数据
    def saveUrlListResp(self, urlList):
        dataPath = os.path.join(self.__tempPath, "data"); # 数据路径
        if not os.path.exists(dataPath):
            os.makedirs(dataPath);
        with open(os.path.join(dataPath, urlListName), "w") as f:
            f.write(json.dumps(urlList));
    def onComplete(self, version):
        self.__du.forget();
        self.__tipsVal.set(f"平台【{version}】下载安装完成！\n安装路径为："+self.__tempPath);
        pass;
    def verifyPath(self):
        self.__tipsVal.set(f"开始校验平台资源文件...");
        verifyAssets(self.__tempPath, self.__basePath, getDependMapPath(self.__projectPath))
        self.__tipsVal.set(f"完成平台资源文件校验。\n开始更新平台目录..");
        if os.path.exists(self.__updatePath):
            shutil.rmtree(self.__updatePath);
        shutil.move(self.__tempPath, self.__updatePath);
        self.__tipsVal.set(f"完成平台目录更新。");
        pass;
    def showFailedTips(self, tips):
        self.__du.forget();
        self.__tips.pack(pady = (80, 10));
        self.__tipsVal.set(tips);
        self.__reUpdateBtn.pack(pady = (40, 10));
    def reUpdate(self):
        self.__tips.forget();
        self.__reUpdateBtn.forget();
    def getUrlKeyMap(self, urlList):
        keyMap = {};
        for urlInfo in urlList:
            keyMap[urlInfo.get("type", "") + urlInfo.get("name", "")] = urlInfo;
        return keyMap;
    def checkUrlList(self, urlList):
        keyMap = self.getUrlKeyMap(urlList);
        baseKeyMap = {};
        urlListPath = getUrlListPath(self.__basePath);
        if os.path.exists(urlListPath):
            with open(urlListPath, "r") as f:
                baseJson = json.loads(f.read());
                baseKeyMap = self.getUrlKeyMap((baseJson.get("urlList")));
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

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        sys.exit(1);
    # 加载程序
    App = MainApp();
    # 加载主场景
    MainWindow(App, *sys.argv[1:]);
    # 运行程序
    App.mainloop();
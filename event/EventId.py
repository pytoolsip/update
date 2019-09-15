# -*- coding: utf-8 -*-
# @Author: JimDreamHeart
# @Date:   2018-04-01 10:56:10
# @Last Modified by:   JinZhang
# @Last Modified time: 2019-03-29 17:34:37

from enum import Enum, unique;

# 自增的事件Id函数
global CUR_EVENT_ID;
CUR_EVENT_ID = -1;
def getNewEventId():
	global CUR_EVENT_ID;
	CUR_EVENT_ID += 1;
	return CUR_EVENT_ID;

# 枚举事件Id
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
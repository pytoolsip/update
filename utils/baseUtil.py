# 销毁控制类【需先销毁UI】（视图或窗口）
def DelCtr(ctr):
	Del(ctr.getUI());
	Del(ctr);

# 主动销毁类
def Del(obj):
	if hasattr(obj, "__dest__"):
		obj.__dest__();
	del obj;
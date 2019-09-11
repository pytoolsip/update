from tkinter import *;
from tkinter import ttk;
from tkinter import messagebox;
import os;
import shutil;

from config.AppConfig import *; # local
from event.Instance import *; # local

from view.VerSelector import *; # local
from view.DownloadUnZip import *; # local

class MainWindow(Frame):
    def __init__(self, parent):
        super(MainWindow, self).__init__(parent);
        self.__parent = parent;
        self.__thread = None;
        self.__basePath = "";
        self.pack(expand = YES, fill = BOTH);
        self.initWindow();
        self.registerEvent();

    def __del__(self):
        self.stopThread();
        self.unregisterEvent();

    def onDestroy(self, data):
        if self.__thread: # 判断下载线程是否还存在
            if messagebox.askokcancel(title="取消更新", message="正在下载更新中，是否确定要取消本次更新？"):
                self.stopThread(); # 停止子线程
                # 移除更新路径内容
                if self.__basePath and os.path.exists(self.__basePath):
                    shutil.rmtree(self.__basePath);
                    self.__basePath = "";

    def registerEvent(self):
        EventSystem.register(EventID.WM_DELETE_WINDOW, self, "onDestroy");

    def unregisterEvent(self):
        EventSystem.unregister(EventID.WM_DELETE_WINDOW, self, "onDestroy");

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
        # 初始化下拉框
        self.__vc = VerSelector(f);
        self.__vc.pack(expand = YES, fill = BOTH);
        # self.__vc.forget();
        # 点击更新回调
        self.__vc.onUpdate = self.onUpdate;
        # 初始化下载进度条
        self.__du = DownloadUnZip(f);
        self.__du.forget();
        # 初始化提示信息
        self.__tipsVal = StringVar();
        self.__tips = Label(f, textvariable=self.__tipsVal, font=("宋体", 10), bg= AppConfig["ContentColor"]);
        self.__tips.pack(pady = (80, 10));
        # 初始化重新更新按钮
        self.__reUpdateBtn = Button(f, text="点击重新更新", command=self.reUpdate);
        self.__reUpdateBtn.forget();
        pass;
    
    def onUpdate(self, path, version):
        self.__basePath = os.path.join(path, "PyToolsIP"); # 重置基本路径
        if not os.path.exists(self.__basePath):
            os.makedirs(self.__basePath);
        self.__vc.forget();
        self.downloadIPByThread(version);

    # 启动新线程下载平台
    def downloadIPByThread(self, version):
        # print("downloadIP:", self.__basePath, version);
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
            urlList = resp.get("urlList", []);
            if len(urlList) > 0:
                self.saveUrlList(urlList);
                def onComplete():
                    self.onComplete(version);
                self.__du.start(urlList, self.__basePath, onComplete = onComplete);
            else:
                messagebox.showerror(title="数据异常", message="下载平台失败！");
                self.showFailedTips("平台数据异常，下载平台失败！");
        else:
            messagebox.showerror(title="网络异常", message="下载平台失败！");
            self.showFailedTips("网络连接异常，下载平台失败！");
        # 置空线程对象
        self.__thread = None;

    # 保存url列表数据
    def saveUrlList(self, urlList):
        dataPath = os.path.join(self.__basePath, "data"); # 数据路径
        if not os.path.exists(dataPath):
            os.makedirs(dataPath);
        with open(os.path.join(dataPath, "url_list.json"), "w") as f:
            f.write(json.dumps(urlList));

    def onComplete(self, version):
        self.__du.forget();
        self.__tips.pack(pady = (80, 10));
        self.__tipsVal.set(f"平台【{version}】下载安装完成！\n安装路径为：{self.__basePath}");
        pass;

    def onCopyPath(self):
        pass;

    def showFailedTips(self, tips):
        self.__du.forget();
        self.__tips.pack(pady = (80, 10));
        self.__tipsVal.set(tips);
        self.__reUpdateBtn.pack(pady = (40, 10));

    def reUpdate(self):
        self.__tips.forget();
        self.__reUpdateBtn.forget();
        self.__vc.pack(expand = YES, fill = BOTH);
        

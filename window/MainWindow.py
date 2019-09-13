from tkinter import *;
from tkinter import ttk;
from tkinter import messagebox;
import os;
import shutil;
import time;

from config.AppConfig import *; # local
from event.Instance import *; # local

from view.VerSelector import *; # local
from view.DownloadUnZip import *; # local

urlListName = "url_list.json"
def getUrlListPath(basePath):
    return os.path.join(basePath, "data", urlListName);

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
            # self.__parent.onDestroy();
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
                    self.saveUrlListResp(resp);
                    self.renamePath();
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
        self.__tips.pack(pady = (80, 10));
        self.__tipsVal.set(f"平台【{version}】下载安装完成！\n安装路径为：{self.__tempPath}");
        pass;

    def renamePath(self):
        if os.path.exists(self.__updatePath):
            shutil.rmtree(self.__updatePath);
        shutil.move(self.__tempPath, self.__updatePath);
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
        

import wx
import time;
import os;
import base64;
import shutil;

from event.Instance import *; # local
from config.AppConfig import *; # local
from utils.urlUtil import *; # local
from utils.updateUtil import *; # local

from window.MainWindow.MainWindowCtr import *; # local

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
    def create(self):
        self.__mainWinCtr = MainWindowCtr(self);

    # 执行程序
    def run(self):
        self.__isRunning = True;
        self.verifyPath();
        self.downloadIP();

    def onFinish(self):
        self.__isRunning = False;

    def verifyPath(self):
        if os.path.exists(getUrlListPath(self.__updatePath)):
            self.__basePath = self.__updatePath;
        elif os.path.exists(getUrlListPath(self.__projectPath)):
            self.__basePath = self.__projectPath;
        if not self.__basePath:
            # self.onQuit();
            return;
        if os.path.exists(self.__tempPath):
            shutil.rmtree(self.__tempPath);
        os.makedirs(self.__tempPath);

    # 下载平台
    def downloadIP(self):
        ret, resp = requestJson({"key":"ptip", "req":"urlList", "version":version});
        if ret:
            urlList = self.checkUrlList(resp.get("urlList", []));
            if len(urlList) > 0:
                self.createTasks(urlList);
                def onComplete():
                    self.saveUrlListResp(resp);
                    self.onFinish();
                EventSystem.dispatch(EventID.START_SCHEDULE_TASK, {
                    "callbackInfo" : {"callback" : onComplete},
                });
            else:
                wx.MessageDialog(self.__mainWinCtr.getUI(), "下载平台失败！", "数据异常", style = wx.OK|wx.ICON_ERROR).ShowModal();
        else:
            wx.MessageDialog(self.__mainWinCtr.getUI(), "下载平台失败！", "网络异常", style = wx.OK|wx.ICON_ERROR).ShowModal();

    # 创建任务
    def createTasks(self, urlList):
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

    # 保存url列表数据
    def saveUrlListResp(self, urlList):
        dataPath = os.path.join(self.__tempPath, "data"); # 数据路径
        if not os.path.exists(dataPath):
            os.makedirs(dataPath);
        with open(os.path.join(dataPath, urlListName), "w") as f:
            f.write(json.dumps(urlList));

    def verifyPath(self):
        self.__tipsVal.set(f"开始校验平台资源文件...");
        verifyAssets(self.__tempPath, self.__basePath, getDependMapPath(self.__projectPath))
        self.__tipsVal.set(f"完成平台资源文件校验。\n开始更新平台目录..");
        if os.path.exists(self.__updatePath):
            shutil.rmtree(self.__updatePath);
        shutil.move(self.__tempPath, self.__updatePath);
        self.__tipsVal.set(f"完成平台目录更新。");

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

    # 下载文件
    def __download__(self, url, filepath, addGaugeVal = None):
        self.__tips.set(f"正在下载：\n{url}");
        self.__checkFilePath__(filepath);
        def schedule(block, size, totalSize):
            addGaugeVal(block*size / totalSize);
        request.urlretrieve(url, filepath, schedule);

    # 解压文件
    def __unzip__(self, filepath, dirpath, isRmZip = True, addGaugeVal = None):
        if not os.path.exists(filepath):
            return;
        with zipfile.ZipFile(filepath, "r") as zf:
            totalCnt = len(zf.namelist());
            completeCnt = 0;
            for file in zf.namelist():
                zf.extract(file, dirpath);
                completeCnt += 1;
                addGaugeVal(completeCnt/totalCnt);
            zf.close();
            # 移除zip文件
            if isRmZip:
                os.remove(filepath);

import wx
import time;
import os;
import base64;
import shutil;
import zipfile;

from event.Instance import *; # local
from config.AppConfig import *; # local
from utils.urlUtil import *; # local
from utils.updateUtil import *; # local

from window.MainWindow.MainWindowCtr import *; # local

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
            oriUrlList = resp.get("urlList", []);
            urlList = self.checkUrlList(oriUrlList);
            if len(urlList) > 0:
                self.saveUrlListResp(resp); # 保存请求数据
                self.createTasks(self.__tempPath, urlList, oriUrlList); # 创建任务
                EventSystem.dispatch(EventID.START_SCHEDULE_TASK, {
                    "callbackInfo" : {"callback" : self.onFinish},
                });
            else:
                wx.MessageDialog(self.__mainWinCtr.getUI(), "下载平台失败！", "数据异常", style = wx.OK|wx.ICON_ERROR).ShowModal();
        else:
            wx.MessageDialog(self.__mainWinCtr.getUI(), "下载平台失败！", "网络异常", style = wx.OK|wx.ICON_ERROR).ShowModal();

    # 创建任务
    def createTasks(self, basePath, urlList, oriUrlList):
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
        # 添加校验更新目录任务
        EventSystem.dispatch(EventID.ADD_SCHEDULE_TASK, {
            "scheduleTask" : self.__verifyUrlList__,
            "text" : f"正在校验更新目录{self.__updatePath}",
            "args" : {
                "list" : [oriUrlList],
            },
            "failInfo" : {
                "text" : f"校验更新目录{self.__updatePath}失败！",
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

    def __verifyUrlList__(self, urlList, callback = None):
        count = 0;
        for urlInfo in urlList:
            name = urlInfo.get("name", "");
            fileName = os.path.basename(urlInfo["url"]);
            _, ext = os.path.splitext(fileName);
            if name:
                filepath = os.path.join(checkPath(urlInfo["path"]), name);
                if ext != ".zip":
                    filepath += ext;
            else:
                filepath = os.path.join(checkPath(urlInfo["path"]), fileName);
            tempPath = os.path.abspath(os.path.join(self.__tempPath, filepath));
            updatePath = os.path.abspath(os.path.join(self.__updatePath, filepath));
            if not os.path.exists(tempPath) and os.path.exists(updatePath):
                shutil.move(updatePath, tempPath);
                pass;
            # 自增计数
            count += 1;
            callback(count/len(urlList));
        return True;
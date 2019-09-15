import sys;
from tkinter import *

from window.MainApp import *; # local

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        sys.exit(1);
    # 加载程序
    App = MainApp(*sys.argv[1:]);
    # 创建窗口
    App.create();
    # 执行程序
    App.run();
    # 运行程序
    App.MainLoop();
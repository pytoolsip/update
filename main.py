import sys;
from tkinter import *

from window.MainApp import *; # local
from window.MainWindow import *; # local

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        sys.exit(1);
    # 加载程序
    App = MainApp();
    # 加载主场景
    MainWindow(App, *sys.argv[1:]);
    # 运行程序
    App.mainloop();
from urllib import request
import json

from config.AppConfig import *; # local

# 请求json数据
def requestJson(url, data):
    kv = [];
    for k,v in data.items():
        kv.append(f"{k}={v}");
    try:
        resp = request.urlopen(f"{url}?"+"&".join(kv));
        return True, json.loads(resp.read());
    except Exception as e:
        print(e);
    return False, None;
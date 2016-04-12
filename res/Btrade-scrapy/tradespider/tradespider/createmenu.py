# -*- coding: utf-8 -*-
import requests,json


if __name__ == '__main__':
    url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx90e04052c49aa63e&secret=b1146d3ec7e0a8a483064406f361a07b"
    res = requests.get(url)
    message = json.loads(res.text.encode("utf-8"))
    print message
    url = "https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % message["access_token"]
    payload = {
        "button":[
        {
             "type":"view",
             "name":"去报价",
             "url":"http://m.yaocai.pro"
         },
        {
             "type":"view",
             "name":"发采购",
             "url":"http://m.yaocai.pro/yaocaigou"
         },
        {
             "type":"view",
             "name":"我的工作台",
             "url":"http://m.yaocai.pro/center"
         }
         ]
    }
    res = requests.post(url,data=payload)
    r = json.loads(res.text.encode("utf-8"))
    print r
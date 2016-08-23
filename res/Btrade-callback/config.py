# -*- coding: utf-8 -*-
import os.path
from handler.smshook import *
from globalconfig import *



settings = {
    "app": app,
    "xsrf_cookies": False,
    "cookie_secret": "e446976943b4e8442f099fed1f3fea28462d5832f483a0ed9a3d5d3859f==78d",
    "session_secret": "3cdcb1f00803b6e78ab50b466a40b9977db396840c28307f428b25e2277f1bcc",
    "session_timeout": 60*60,
    "store_options": {
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_pass': '',
    },
}

handlers = [
    (r"/pushpurchase/smshook", SmsHookHandler),
    (r"/alipay/notify", AlipayNotifyHandler),
];


"""日志设置
开启多个实例时请使用 -log_file_prefix='log@8000.txt' 命令参数，
每个端口需要单独定义。
此时该设置将无任何作用
"""
#开启日志文件记录，默认为 False
log = True
#日志记录位置
log_file = 'Btrade-callback/log/tornado.log'




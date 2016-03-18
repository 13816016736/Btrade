# -*- coding: utf-8 -*-
import os.path
from handler.main import *
from handler.login import *
from handler.purchase import *

#显示设置
app = {
    #应用名称
    'name': '药采购',
    #应用附加信息(简短的说明)
    'title': '药材买卖的专业助手',
    #联系邮箱
    'email': '2011zhouhang@gmail.com',
}

settings = {
    "app": app,
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "xsrf_cookies": True,
    "login_url": "/login",
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
    (r"/", MainHandler),
    (r"/users/userlist", UserListHandler),
    (r"/users/userlist/page/([0-9]+)", UserListHandler),
    (r"/users/userinfo", UserInfoHandler),
    (r"/users/userinfo/([0-9]+)", UserInfoHandler),
    (r"/users/recover/([0-9]+)", UserRecoverHandler),
    (r"/users/remove/([0-9]+)", UserRemoveHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/purchase/purchaselist/type/(-?[0-9]+)/starttime/(.*)/endtime/(.*)/page/([0-9]+)", PurchaseHandler),
    (r"/purchase/purchaselist/type/(-?[0-9]+)/starttime/(.*)/endtime/(.*)", PurchaseHandler),
    (r"/purchase/purchaseinfo/([0-9]+)", PurchaseInfoHandler),
    (r"/updatequotestate", UpdateQuoteStateHandler),
    (r"/removepurchase", RemovePurchaseHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
];

#参数配置项
#如果设置为0则不现实，此处的更改为全局设置，但仍然可以单独设置某处的显示选项
conf = {
    #主页显示的文章数目
    'POST_NUM': 10,
}

"""日志设置
开启多个实例时请使用 -log_file_prefix='log@8000.txt' 命令参数，
每个端口需要单独定义。
此时该设置将无任何作用
"""
#开启日志文件记录，默认为 False
log = False
#日志记录位置
log_file = 'log/tornado.log'

#用户密码的salt
salt = "ycg20151012"

#图片服务器域名
img_domain = "http://10.0.24.147/"
img_path = "E:\\wamp\\www\\static\\uploadfiles\\"
# img_path = "F:\\nginx-1.8.1\\html\\static\\uploadfiles"
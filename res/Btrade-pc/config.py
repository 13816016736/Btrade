# -*- coding: utf-8 -*-
import os.path
from handler.main import *
from handler.login import *
from handler.purchase import *
from handler.register import *
from handler.dashboard import *
from handler.supplier import *
from globalconfig import *



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
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/register", RegisterHandler),
    (r"/getsmscode", GetSmsCodeHandler),
    (r"/register/checkphone", CheckPhoneHandler),
    (r"/reginfo", RegInfoHandler),
    (r"/regresult", RegResultHandler),
    (r"/purchase", PurchaseHandler),
    (r"/getparentarea", GetParentAreaHandler),
    (r"/uploadfile", UploadFileHandler),
    (r"/delfile", DeleteFileHandler),
    (r"/getvarietyinfo", GetVarietyInfoHandler),
    (r"/getvarinfobyid", GetVarInfoByIdHandler),
    (r"/purchasesuccess", PurchaseSuccessHandler),
    (r"/dashboard", DashboardHandler),
    (r"/supplier/detail", SupplierDetailHandler),
    (r"/supplier", SupplierHandler),
    (r"/payment", PaymentHandler),
    (r"/alipay/return", AlipayReturnHandler),
    (r"/sunshine", SunshineHandler),
    #(r"/mypurchase/type/(-?[0-9]+)/starttime/(.*)/endtime/(.*)/page/([0-9]+)", MyPurchaseHandler),
    #(r"/mypurchase/type/(-?[0-9]+)/starttime/(.*)/endtime/(.*)", MyPurchaseHandler),
    (r"/mypurchase", MyPurchaseHandler),
    (r"/mypurchase/update/([0-9]+)", MyPurchaseUpdateHandler),
    (r"/removepurchase", RemovePurchaseHandler),
    (r"/mypurchase/info/([0-9]+)", MyPurchaseInfoHandler),
    (r"/updatequotestate", UpdateQuoteStateHandler),
    (r"/account", AccountHandler),
    (r"/updateuser", UpdateUserHandler),
    (r"/updateusername", UpdateUserNameHandler),
    (r"/updateuserinfo", UpdateUserInfoHandler),
    (r"/contact", ContactHandler),
    (r"/aboutus", AboutusHandler),
    (r"/quote", QuoteHandler),
    (r"/forgetpwd", ForgetPwdHandler),
    (r"/setpwd", SetPwdHandler),
    (r"/getsmscodeforpwd", GetSmsCodeForPwdHandler),
    (r"/getSupplier", GetSupplierHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
    (r".*", BaseHandler),
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
log = True
#日志记录位置
log_file = 'Btrade-pc/log/tornado.log'



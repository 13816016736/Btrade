# -*- coding: utf-8 -*-
import os.path
from handler.main import *
from handler.login import *
from handler.register import *
from handler.purchase import *
from handler.quote import *

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
    (r"/purchase/purchaselist", PurchaseHandler),
    (r"/purchase/purchaselist/number/([0-9]+)", PurchaseHandler),
    (r"/purchase/purchaseinfo/([0-9]+)", PurchaseInfoHandler),
    (r"/purchaseinfobatch/purchaseid/([0-9]+)", PurchaseinfoBatchHandler),
    (r"/removepurchase", RemovePurchaseHandler),
    (r"/updatequotestate", UpdateQuoteStateHandler),
    (r"/yaocaigou", YaocaigouHandler),
    (r"/center", CenterHandler),
    (r"/user/attention", UserAttentionHandler),
    (r"/user/updatepassword", UserUpdatePasswordHandler),
    (r"/user/updatenickname", UserUpdateNicknameHandler),
    (r"/user/category", UserCategoryHandler),
    (r"/userinfo", UserInfoHandler),
    (r"/news/type/([0-9]+)", NewsHandler),
    (r"/news/articleid/([0-9]+)", ArticleHandler),
    (r"/quote", QuoteHandler),
    (r"/quote/purchaseinfoid/([0-9]+)", QuoteHandler),
    (r"/quote/upload/purchaseinfoid/([0-9]+)/type/([0-9]+)", QuoteUploadHandler),
    (r"/quotesuccess", QuoteSuccessHandler),
    (r"/quotedetail/quoteid/([0-9]+)/nid/([0-9]+)", QuoteDetailHandler),
    (r"/quotelist", QuoteListHandler),
    (r"/weixin", WeixinHandler),
    (r"/uploadfile", UploadFileHandler),
    (r"/delfile", DeleteFileHandler),
    (r"/users/userinfo/([0-9]+)", UserInfoHandler),
    (r"/login", LoginHandler),
    (r"/bindwx", BindWxHandler),
    (r"/logout", LogoutHandler),
    (r"/register", RegisterHandler),
    (r"/register/next_url/(.*)", RegisterHandler),
    (r"/getsmscode", GetSmsCodeHandler),
    (r"/regsuccess", RegSuccessHandler),
    (r"/getvarietyinfo", GetVarietyInfoHandler),
    (r"/savevariety", SaveVarietyHandler),
    (r"/wxcb", WxcbHandler),
    (r"/wechartconfig", WechartConfigHandler),
    (r"/forgetpwd", ForgetPwdHandler),
    (r"/setpwd", SetPwdHandler),
    (r"/getsmscodeforpwd", GetSmsCodeForPwdHandler),
    (r"/reply", ReplayHandler),
    (r"/replydetail", ReplayDetailHandler),
    (r"/variety", VarietySearchHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "./static"}),
    (r".*", BaseHandler),
];

#参数配置项
#如果设置为0则不现实，此处的更改为全局设置，但仍然可以单独设置某处的显示选项
conf = {
    #主页显示的文章数目
    'POST_NUM': 5,
    #每周能报价的次数
    'QUOTE_NUM': 20,
}

"""日志设置
开启多个实例时请使用 -log_file_prefix='log@8000.txt' 命令参数，
每个端口需要单独定义。
此时该设置将无任何作用
"""
#开启日志文件记录，默认为 False
log = True 
#日志记录位置
log_file = 'Btrade-mobile/log/tornado.log'




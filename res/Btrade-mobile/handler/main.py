# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import config
import json, os, datetime
import time
from collections import defaultdict
from utils import *
from wechatjsapi import *

class MainHandler(BaseHandler):

    def get(self):
        varieties = []
        quotevariety = []
        userid = self.session.get("userid")
        if userid:
            user = self.db.get("select varietyids from users where id = %s", userid)
            if user["varietyids"]:
                varieties = self.db.query("select name from variety where id in (" + user["varietyids"] + ")")

            #用户报过价的品种
            quotevariety = self.db.query("select v.name name from (select pi.varietyid from quote q left join purchase_info pi on q.purchaseinfoid = pi.id where userid = %s) t"
                          " left join variety v on t.varietyid = v.id group by name", userid)

        self.render("index.html", varieties=varieties, quotevariety=quotevariety)


    def post(self):
        pass

class YaocaigouHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("yaocaigou.html")

class CenterHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.db.get("select * from users where id = %s", self.session.get("userid"))
        news = self.db.query("select * from notification where receiver = %s order by createtime desc", self.session.get("userid"))

        unread = 0
        unreadtype = 0
        sell = []
        purchase = []
        quoteid = []
        for new in news:
            if new.status == 0:
                unread += 1
                unreadtype = new.type
            if new.type == 1:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                if new["content"].isdigit():
                    quoteid.append(new["content"])
                sell.append(new)
            if new.type == 2:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                purchase.append(new)
        #更新session中未读信息数
        self.session["notification"] = unread
        self.session.save()

        #报价收到回复消息的表情
        results = []
        if quoteid:
            results = self.db.query("select id,state from quote where userid = %s and id in ("+",".join(quoteid)+")", self.session.get("userid"))
        faces = {}
        for result in results:
            faces[str(result["id"])] = int(result["state"])
        print faces
        #最近一周报价次数
        t = time.time()
        week_begin = get_week_begin(t,0)
        week_end = get_week_begin(t,1)
        quotecount = self.db.execute_rowcount("select id from quote where userid = %s and createtime > %s and createtime < %s"
                                 , self.session.get("userid"), week_begin,week_end)

        self.render("center.html", user=user, unread=unread, unreadtype=unreadtype, sell=sell, purchase=purchase, faces=faces, quotecount=quotecount)

    @tornado.web.authenticated
    def post(self):
        pass

class UserAttentionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, page=0):
        userid = self.session.get("userid")
        user = self.db.get("select varietyids from users where id = %s", userid)
        varieties = []
        if user["varietyids"]:
            varieties = self.db.query("select id,name from variety where id in (" + user["varietyids"] + ")")
        self.render("user_attention.html", varieties=varieties)

class UserInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user = self.db.get("SELECT * FROM users where id = %s", self.session.get("userid"))
        varieties = []
        if user["varietyids"]:
            varieties = self.db.query("select name from variety where id in (" + user["varietyids"] + ")")
        self.render("user_info.html", user=user, varieties=varieties)

    @tornado.web.authenticated
    def post(self):
        pass

class NewsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, type):
        news = self.db.query("select * from notification where receiver = %s order by createtime desc", self.session.get("userid"))
        unread = {}
        sell = []
        purchase = []
        grow = []
        system = []
        quoteid = []
        for new in news:
            if new.status == 0:
                if new.type == 1:
                    unread["sell"] = True
                elif new.type == 2:
                    unread["purchase"] = True
                elif new.type == 3:
                    unread["grow"] = True
                elif new.type == 4:
                    unread["system"] = True
            if new.type == 1:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                if new["content"].isdigit():
                    quoteid.append(new["content"])
                sell.append(new)
            if new.type == 2:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                purchase.append(new)
            if new.type == 3:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                grow.append(new)
            if new.type == 4:
                new["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(new["createtime"])))
                system.append(new)
        #报价收到回复消息的表情
        results = []
        if quoteid:
            results = self.db.query("select id,state from quote where userid = %s and id in ("+",".join(quoteid)+")", self.session.get("userid"))
        faces = {}
        for result in results:
            faces[str(result["id"])] = int(result["state"])
        print faces
        self.render("news.html", type=int(type), unread=unread, sell=sell, purchase=purchase, grow=grow, system=system, faces=faces)

    @tornado.web.authenticated
    def post(self):
        pass

class ArticleHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, articleid):
        article = self.db.get("select * from notification where receiver = %s and id = %s", self.session.get("userid"), articleid)
        result = self.db.execute("update notification set status = 1 where receiver = %s and id = %s", self.session.get("userid"), articleid)
        print result
        article["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(article["createtime"])))
        self.render("article.html", article=article)

    @tornado.web.authenticated
    def post(self):
        pass

class UserUpdatePasswordHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('update_password.html')

    @tornado.web.authenticated
    def post(self):
        userid = self.session.get("userid")
        author = self.db.get("SELECT * FROM users WHERE id = %s", userid)
        if not author:
            self.api_response({'status':'faile','message':'用户名不存在'})
        elif self.get_argument("oldpassword") == "" or self.get_argument("password") == "" or self.get_argument("passwordconfirm") == "":
            self.api_response({'status':'fail','message':'新旧密码必须填写'})
        elif self.get_argument("password") != self.get_argument("passwordconfirm"):
            self.api_response({'status':'fail','message':'新密码和确认密码不一致'})
        elif md5(str(self.get_argument("oldpassword")+config.salt)) != author.password:
            self.api_response({'status':'fail','message':'旧密码不对'})
        else:
            self.db.update("UPDATE users SET password = %s  WHERE id = %s", md5(str(self.get_argument("password")+config.salt)), userid)
            self.api_response({'status':'success','message':'更新成功'})

class UserUpdateNicknameHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        user = self.db.get("SELECT * FROM users WHERE id = %s", userid)
        self.render('update_nickname.html', user=user)

    @tornado.web.authenticated
    def post(self):
        nickname = self.get_argument("nickname")
        if nickname:
            self.db.update("UPDATE users SET nickname = %s  WHERE id = %s", nickname, self.session.get("userid"))
            self.api_response({'status':'success','message':'更新成功'})
        else:
            self.api_response({'status':'fail','message':'个人称呼必填'})

class UserCategoryHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        user = self.db.get("SELECT * FROM users WHERE id = %s", userid)
        self.render('category.html', user=user)

    @tornado.web.authenticated
    def post(self):
        type = self.get_argument("type")
        if type:
            self.db.update("UPDATE users SET type = %s  WHERE id = %s", type, self.session.get("userid"))
            self.api_response({'status':'success','message':'更新成功'})
        else:
            self.api_response({'status':'fail','message':'请选择经营类型'})

class WxcbHandler(BaseHandler):
    def get(self):
        signature = self.get_argument("signature")
        timestamp = self.get_argument("timestamp")
        nonce = self.get_argument("nonce")
        echostr = self.get_argument("echostr")

        if checkSignature(signature, timestamp, nonce):
            self.api_response(echostr)
        else:
            self.api_response("check signature fail")

class WechartConfigHandler(BaseHandler):
    def post(self):
        wechart = WechartJSAPI(self.db).sign(self.get_argument("url",None))
        if wechart:
            self.api_response({'status':'success','message':'获取微信配置成功','data':wechart})
        else:
            self.api_response({'status':'fail','message':'获取微信配置失败'})
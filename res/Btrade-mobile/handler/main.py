# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import config
import json, os, datetime
import time
from collections import defaultdict

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        user = self.db.get("select varietyids from users where id = %s", userid)
        varieties = self.db.query("select name from variety where id in (" + user["varietyids"] + ")")

        purchaseinf = defaultdict(list)
        purchases = self.db.query("select t.*,a.areaname from (select p.*,u.nickname,u.name,u.type from purchase p left join users u on p.userid = u.id order by p.createtime desc limit 0,5) t left join area a on t.areaid = a.id")
        if purchases:
            purchaseids = [str(purchase["id"]) for purchase in purchases]
            purchaseinfos = self.db.query("select p.*,s.specification from purchase_info p left join specification s on p.specificationid = s.id where p.purchaseid in ("+",".join(purchaseids)+")")
            purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
            purchaseattachments = self.db.query("select * from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
            attachments = defaultdict(list)
            for attachment in purchaseattachments:
                attachments[attachment["purchase_infoid"]] = attachment
            for purchaseinfo in purchaseinfos:
                purchaseinfo["attachments"] = attachments.get(purchaseinfo["id"])
                purchaseinf[purchaseinfo["purchaseid"]].append(purchaseinfo)
        for purchase in purchases:
            purchase["purchaseinfo"] = purchaseinf.get(purchase["id"]) if purchaseinf.get(purchase["id"]) else []
            purchase["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchase["createtime"])))
            if purchase["limited"] == 1:
                purchase["expire"] = datetime.datetime.utcfromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
                purchase["timedelta"] = (purchase["expire"] - datetime.datetime.now()).days
        print purchases

        self.render("index.html", varieties=varieties, purchases=purchases)

class YaocaigouHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("yaocaigou.html")

class CenterHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("center.html")

    @tornado.web.authenticated
    def post(self):
        pass

class UserAttentionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, page=0):
        userid = self.session.get("userid")
        user = self.db.get("select varietyids from users where id = %s", userid)
        varieties = self.db.query("select id,name from variety where id in (" + user["varietyids"] + ")")
        self.render("user_attention.html", varieties=varieties)

class UserListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, page=0):
        page = (int(page) - 1) if page > 0 else 0
        nav = {
            'model': 'users/userlist',
            'num': self.db.execute_rowcount("SELECT * FROM users"),
        }
        users = self.db.query("SELECT * FROM users LIMIT %s,%s", page * config.conf['POST_NUM'], config.conf['POST_NUM'])
        self.render("userlist.html", users=users, nav=nav)

class UserInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        user = self.db.get("SELECT * FROM users where id = %s", self.session.get("userid"))
        varieties = self.db.query("select name from variety where id in (" + user["varietyids"] + ")")
        self.render("user_info.html", user=user, varieties=varieties)

    @tornado.web.authenticated
    def post(self):
        pass

class NewsHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, type=1):
        print type
        self.render("news.html")

    @tornado.web.authenticated
    def post(self):
        pass

class UserRecoverHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userid):
        self.db.execute("update users set status=1 where id = %s", userid)
        self.redirect('/users/userlist')

class UserRemoveHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userid):
        self.db.execute("update users set status=0 where id = %s", userid)
        self.redirect('/users/userlist')
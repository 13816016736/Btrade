# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import config

class MainHandler(BaseHandler):
    def get(self):
        self.redirect('/users/userlist')
        # self.render("main.html")

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
    def get(self, userid):
        user = self.db.get("SELECT * FROM users where id = %s", userid)
        self.render("userinfo.html", user=user)

    @tornado.web.authenticated
    def post(self):
        if self.get_argument("userid") is None or self.get_argument("nickname") is None or self.get_argument("type") is None or self.get_argument("name") is None or self.get_argument("phone") is None:
            self.api_response({'status':'fail','message':'请完整填写表单'})
        else:
            self.db.execute("update users set nickname=%s,type=%s,name=%s,phone=%s where id = %s",
                            self.get_argument("nickname"), self.get_argument("type"), self.get_argument("name"),
                            self.get_argument("phone"), self.get_argument("userid"))
            self.api_response({'status':'success','message':'提交成功'})

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

class UpdateQuoteStateHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        qid = str(self.get_argument("qid", 0))
        state = str(self.get_argument("state", 0))
        if qid != 0 and state !=0:
            self.db.execute("update quote set state=%s where id in ("+qid+")", state)
            self.api_response({'status':'success','message':'操作成功'})
        else:
            self.api_response({'status':'fail','message':'请选择要标注的报价'})
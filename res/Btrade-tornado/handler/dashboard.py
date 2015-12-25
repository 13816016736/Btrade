# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
from utils import *
import config

class DashboardHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("dashboard/main.html")


class AccountHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        provinces = self.db.query("SELECT id,areaname FROM area WHERE parentid = 0")
        users = self.db.query("SELECT * FROM users WHERE id = %s", self.session.get("userid"))
        user_info = self.db.query("SELECT * FROM user_info WHERE userid = %s", self.session.get("userid"))
        if users and user_info:
            users[0].update(user_info[0])
        else:
            users[0]["name"] = ""
        print users[0]
        self.render("dashboard/account.html", user=users[0], provinces=provinces)

class UpdateUserHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        print self.get_argument("oldpassword", None)
        nickname = self.get_argument("nickname")
        userid = self.session.get("userid")
        author = self.db.get("SELECT * FROM users WHERE id = %s", userid)
        if self.get_argument("oldpassword", None) is None and self.get_argument("password", None) is None:
            password = ""
        else:
            if self.get_argument("oldpassword") == "" or self.get_argument("password") == "":
                self.api_response({'status':'fail','message':'新旧密码必须填写'})
            else:
                if not author:
                    self.api_response({'status':'faile','message':'用户名不存在'})
                if md5(str(self.get_argument("oldpassword")+config.salt)) != author.password:
                    self.api_response({'status':'fail','message':'旧密码不对'})
                password = self.get_argument("password")

        if self.get_argument("oldphone", None) is None and self.get_argument("phone", None) is None and self.get_argument("verifycode", None) is None:
            phone = ""
        else:
            if self.get_argument("oldphone") == "" or self.get_argument("phone") == "" or self.get_argument("verifycode") == "":
                self.api_response({'status':'fail','message':'新旧手机号和短信验证码必须填写'})
            else:
                #短信验证码是否正确self.get_argument("verifycode")
                if not author:
                    self.api_response({'status':'fail','message':'用户名不存在'})
                if self.get_argument("oldphone") != author.phone:
                    self.api_response({'status':'fail','message':'旧手机号不对'})
                phone = self.get_argument("phone")

        if password and phone:
            self.db.query("UPDATE users SET nickname = %s, password = %s, phone = %s  WHERE id = %s", nickname, password, phone, userid)
            self.api_response({'status':'success','message':'更新成功'})
        elif password:
            self.db.query("UPDATE users SET nickname = %s, password = %s  WHERE id = %s", nickname, password, userid)
            self.api_response({'status':'success','message':'更新成功'})
        elif phone:
            self.db.query("UPDATE users SET nickname = %s, phone = %s  WHERE id = %s", nickname, phone, userid)
            self.api_response({'status':'success','message':'更新成功'})
        else:
            self.db.query("UPDATE users SET nickname = %s  WHERE id = %s", nickname, userid)
            self.api_response({'status':'success','message':'更新成功'})

class UpdateUserNameHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        if self.get_argument("name", None) is None:
            self.api_response({'status':'fail','message':'经营主体必填'})
        else:
            self.db.query("UPDATE user_info SET name = %s  WHERE id = %s", self.get_argument("name"), self.session.get("userid"))
            self.api_response({'status':'success','message':'更新成功'})

class UpdateUserInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        if self.get_argument("name", None) is None:
            self.api_response({'status':'fail','message':'经营主体必填'})
        else:
            self.db.query("UPDATE user_info SET name = %s  WHERE id = %s", self.get_argument("name"), self.session.get("userid"))
            self.api_response({'status':'success','message':'更新成功'})

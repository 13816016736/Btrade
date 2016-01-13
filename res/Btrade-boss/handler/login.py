# -*- coding: utf-8 -*-

from base import BaseHandler
from utils import *
import config

class LoginHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.redirect('/users/userlist')
        self.render("login.html", next_url=self.get_argument("next", "/"))

    def post(self):
        username = self.get_argument("username","")
        password = self.get_argument("password","")
        if username == "" or password == "":
            msg = "用户名或密码不能为空"
            self.render("login.html", error="用户名或邮箱不能为空", next_url=self.get_argument("next", "/"))
            return
        author = self.db.get("SELECT * FROM admin WHERE username = %s", username)
        if not author:
            self.render("login.html", error="用户名不存在", next_url=self.get_argument("next", "/")
                        , username=username)
            return
        if md5(str(password+config.salt)) == author.password:
            self.session["adminid"] = author.id
            self.session["admin"] = self.get_argument("username")
            self.session.save()
            self.redirect(self.get_argument("next_url", "/"))
        else:
            self.render("login.html", error="用户名或密码错误", next_url=self.get_argument("next", "/"))

class LogoutHandler(BaseHandler):
    def get(self):
        self.session["adminid"] = ""
        self.session["admin"] = ""
        self.session.save()
        self.redirect('/login')

    def post(self):
        pass

# -*- coding: utf-8 -*-

from base import BaseHandler
from utils import *
import config

class LoginHandler(BaseHandler):
    def get(self):
        if self.current_user:
            self.redirect('/')
        self.render("login.html", next_url=self.get_argument("next", "/"))

    def post(self):
        username = self.get_argument("username","")
        password = self.get_argument("password","")
        if username == "" or password == "":
            msg = "用户名或密码不能为空"
            self.render("login.html", error="用户名或邮箱不能为空", next_url=self.get_argument("next", "/"))
            return
        author = self.db.get("SELECT * FROM users WHERE username = %s", username)
        if not author:
            self.render("login.html", error="用户名不存在", next_url=self.get_argument("next", "/")
                        , username=username)
            return
        if md5(str(password+config.salt)) == author.password:
            notification = self.db.query("select id from notification where receiver = %s", author.id)
            self.session["userid"] = author.id
            self.session["user"] = self.get_argument("username")
            self.session["notification"] = len(notification)
            self.session.save()
            self.redirect(self.get_argument("next_url", "/"))
        else:
            self.render("login.html", error="用户名或密码错误", next_url=self.get_argument("next", "/"))

class LogoutHandler(BaseHandler):
    def get(self):
        self.session["userid"] = ""
        self.session["user"] = ""
        self.session.save()
        self.redirect('/login')

    def post(self):
        pass

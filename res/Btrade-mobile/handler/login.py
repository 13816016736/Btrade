# -*- coding: utf-8 -*-

from base import BaseHandler
from utils import *
import config,re
from webbasehandler import purchase_push_trace

class LoginHandler(BaseHandler):
    @purchase_push_trace
    def get(self):
        if self.current_user:
            self.redirect('/')
        self.render("login.html", next_url=self.get_argument("next", "/"))

    @purchase_push_trace
    def post(self):
        username = self.get_argument("username","")
        password = self.get_argument("password","")
        if username == "" or password == "":
            msg = "用户名或密码不能为空"
            self.render("login.html", error="用户名或邮箱不能为空", next_url=self.get_argument("next_url", "/"))
            return
        #判断是否是手机号登录
        phonepattern = re.compile(r'^1(3[0-9]|4[57]|5[0-35-9]|8[0-9]|7[0-9])\d{8}$')
        phonematch = phonepattern.match(username)
        if phonematch:
            author = self.db.get("SELECT * FROM users WHERE phone = %s", username)
        else:
            author = self.db.get("SELECT * FROM users WHERE username = %s", username)
        if not author:
            self.render("login.html", error="用户名不存在", next_url=self.get_argument("next_url", "/")
                        , username=username)
            return
        if author["status"] == 0:
            self.render("login.html", error="此用户已被禁用，请与客服联系", next_url=self.get_argument("next_url", "/")
                        , username=username)
            return
        if md5(str(password+config.salt)) == author.password:
            notification = self.db.query("select id from notification where receiver = %s", author.id)
            self.session["userid"] = author.id
            self.session["user"] = author.username
            self.session["notification"] = len(notification)
            self.session.save()
            if author.openid!="":
                self.redirect(self.get_argument("next_url", "/"))
            else:
                #ua = self.request.headers['User-Agent']
                #if ua.lower().find("micromessenger") != -1:#微信中就去绑定
                #    self.redirect("https://open.weixin.qq.com/connect/oauth2/authorize?appid=%s&redirect_uri=http://m.yaocai.pro/bindwx&response_type=code&scope=snsapi_base&state=bindwx#wechat_redirect", config.appid)
                #else:
                self.redirect(self.get_argument("next_url", "/"))
        else:
            self.render("login.html", error="用户名或密码错误", next_url=self.get_argument("next_url", "/"))

class LogoutHandler(BaseHandler):
    @purchase_push_trace
    def get(self):
        self.session["userid"] = ""
        self.session["user"] = ""
        self.session.save()
        self.redirect('/login')

    def post(self):
        pass
class BindWxHandler(BaseHandler):
    @purchase_push_trace
    def get(self):
        code = self.get_argument("code", None)
        state= self.get_argument("state", None)
        if code:
            # 请求获取access_token和openid
            url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (
            config.appid, config.secret, code)
            res = requests.get(url)
            message = json.loads(res.text.encode("utf-8"))
            access_token = message.get("access_token", None)
            if access_token :
                openid = message.get("openid")
                if openid :
                    if not self.current_user:
                        userinfo=self.db.query("select id,username from users where openid =%s",openid)
                        if len(userinfo)==1:#只能绑定一个
                            notification = self.db.query("select id from notification where receiver = %s", userinfo[0].id)
                            self.session["userid"] = userinfo[0].id
                            self.session["user"] = userinfo[0].username
                            self.session["notification"] = len(notification)
                            self.session.save()
                    elif state=="bindwx":
                         #绑定微信openid
                         self.db.execute("update users set openid=%s where id=%s", openid,
                                         self.session.get("userid"))

        self.redirect(self.get_argument("next_url", "/"))
    def post(self):
        pass

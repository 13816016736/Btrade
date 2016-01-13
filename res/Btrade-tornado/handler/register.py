# -*- coding: utf-8 -*-

from base import BaseHandler
from uimodule import geetest
import re
from utils import *
import config
import time

#极验证
BASE_URL = "api.geetest.com/get.php?gt="
captcha_id = "9a601256e290cc2001027f5f701a48fb"
private_key = "c7ec51a45463e93b924f0ae462e0cdaa"
product = "embed"

class RegisterHandler(BaseHandler):
    def get(self):
        gt = geetest.geetest(captcha_id, private_key)
        url = ""
        httpsurl = ""
        try:
            challenge = gt.geetest_register()
        except:
            challenge = ""
        if len(challenge) == 32:
            url = "http://%s%s&challenge=%s&product=%s" % (BASE_URL, captcha_id, challenge, product)
            httpsurl = "https://%s%s&challenge=%s&product=%s" % (BASE_URL, captcha_id, challenge, product)
	    self.render("register.html", url=url)

    def post(self):
        username = self.get_argument("username")
        pattern = re.compile(r'^[A-Za-z0-9]{3,20}$')
        match = pattern.match(username)
        if match is False and username is None:
            self.api_response({'status':'fail','message':'会员名填写错误'})
        password = self.get_argument("password")
        repeatpassword = self.get_argument("repeatpassword")
        if password is None and repeatpassword is None and password != repeatpassword:
            self.api_response({'status':'fail','message':'密码和确认密码填写错误'})
        account = self.get_argument("account")
        if account is None:
            self.api_response({'status':'fail','message':'经营主体不能为空'})
        name = self.get_argument("company") if account == 1 else self.get_argument("name")
        if name is None:
            self.api_response({'status':'fail','message':'真实姓名或单位名称不能为空'})
        nickname = self.get_argument("nickname")
        if nickname is None:
            self.api_response({'status':'fail','message':'个人称呼不能为空'})

        lastrowid = self.db.execute_lastrowid("insert into users (username, password, phone, type, name, nickname, status, createtime)"
                             "value(%s, %s, %s, %s, %s, %s, %s, %s)", username, md5(str(password + config.salt)), self.session.get("phone")
                             , account, name, nickname, 1, int(time.time()))
        #因为去掉了user_info表,所以name字段直接放在users表了
        # result = self.db.execute("insert into user_info (userid, name)value(%s, %s)", lastrowid, name)
        self.api_response({'status':'success','message':'注册成功','data':{'username':username}})

class CheckPhoneHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        phone = self.get_argument("phone")
        verifycode = self.get_argument("verifycode")
        challenge = self.get_argument("geetest_challenge")
        validate = self.get_argument("geetest_validate")
        seccode = self.get_argument("geetest_seccode")
        gt = geetest.geetest(captcha_id, private_key)
        result = gt.geetest_validate(challenge, validate, seccode)
        if result:# and verifycode == self.session.get("verifycode"):
            self.session["phone"] = phone
            self.session.save()
            self.api_response({'status':'success','message':'验证成功','data':phone})
        #elif verifycode != self.session.get("verifycode"):
        #    self.api_response({'status':'fail','message':'短信验证码不正确','data':phone})
        else:
            self.api_response({'status':'fail','message':'滑动验证码不正确'})

# -*- coding: utf-8 -*-

from base import BaseHandler
import re,json,config,time,logging
from utils import *

class RegisterHandler(BaseHandler):
    def get(self, next_url="/"):
        userinfo = None
        code = self.get_argument("code", None)
        if code:
            #请求获取access_token和openid
            url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (config.appid, config.secret, code)
            res = requests.get(url)
            message = json.loads(res.text.encode("utf-8"))
            access_token = message.get("access_token", None)
            if access_token:
                openid = message.get("openid")
                #请求获取用户信息
                url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" % (access_token, openid)
                res = requests.get(url)
                userinfo = json.loads(res.text.encode("utf-8"))

	    logging.info(userinfo)
        self.render("register.html", next_url=next_url, userinfo=userinfo)

    def post(self):
        username = self.get_argument("username")
        pattern = re.compile(r'^[A-Za-z0-9]{3,20}$')
        match = pattern.match(username)
        if match is None:
            self.api_response({'status':'fail','message':'会员名填写错误'})
            return
        usercount = self.db.execute_rowcount("select * from users where username = %s", username)
        if usercount > 0:
            self.api_response({'status':'fail','message':'此会员名已被使用'})
            return
        phone = self.get_argument("phone")
        phonepattern = re.compile(r'^1(3[0-9]|4[57]|5[0-35-9]|8[0-9]|7[0-9])\d{8}$')
        phonematch = phonepattern.match(phone)
        if phonematch is None:
            self.api_response({'status':'fail','message':'手机号填写错误'})
            return
        phonecount = self.db.execute_rowcount("select * from users where phone = %s", phone)
        if phonecount > 0:
            self.api_response({'status':'fail','message':'此手机号已被使用'})
            return
        smscode = self.get_argument("smscode")
        if smscode != self.session.get("smscode"):
           self.api_response({'status':'fail','message':'短信验证码不正确','data':phone})
           return

        password = self.get_argument("password")
        repeatpassword = self.get_argument("repeatpassword")
        if password is None and repeatpassword is None and password != repeatpassword:
            self.api_response({'status':'fail','message':'密码和确认密码填写错误'})
            return
        type = self.get_argument("type")
        name = self.get_argument("name")
        if name is None:
            self.api_response({'status':'fail','message':'经营主体不能为空'})
            return
        nickname = self.get_argument("nickname")
        if name is None:
            self.api_response({'status':'fail','message':'真实姓名或单位名称不能为空'})
            return
        nickname = self.get_argument("nickname")
        if nickname is None:
            self.api_response({'status':'fail','message':'个人称呼不能为空'})
            return

        lastrowid = self.db.execute_lastrowid("insert into users (username, password, phone, type, name, nickname, status, openid,createtime)"
                             "value(%s, %s, %s, %s, %s, %s, %s, %s, %s)", username, md5(str(password + config.salt)), phone
                             , type, name, nickname, 1, self.get_argument("openid"), int(time.time()))
        notification = self.db.query("select id from notification where receiver = %s", lastrowid)
        self.session["userid"] = lastrowid
        self.session["user"] = username
        self.session["notification"] = len(notification)
        self.session.save()
        #发短信通知用户注册成功
        regSuccess(phone, name, username)
        self.api_response({'status':'success','message':'注册成功','data':{'username':username}})

class GetSmsCodeHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        phone = self.get_argument("phone")
        phonepattern = re.compile(r'^1(3[0-9]|4[57]|5[0-35-9]|8[0-9]|7[0-9])\d{8}$')
        phonematch = phonepattern.match(phone)
        if phonematch is None:
            self.api_response({'status':'fail','message':'手机号填写错误'})
            return
        phonecount = self.db.execute_rowcount("select * from users where phone = %s", phone)
        if phonecount > 0:
            self.api_response({'status':'fail','message':'此手机号已被使用'})
            return
        smscode = ''.join(random.sample(['0','1','2','3','4','5','6','7','8','9'], 6))
        message = getSmsCode(phone, smscode)
        message = json.loads(message.encode("utf-8"))
        if message["result"]:
            self.session["smscode"] = smscode
            self.session.save()
            self.api_response({'status':'success','message':'短信验证码发送成功，请注意查收'})
        else:
            self.api_response({'status':'fail','message':'短信验证码发送失败，请稍后重试'})

class RegSuccessHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        self.render("register_result.html" ,next_url=self.get_argument("next_url", "/"))

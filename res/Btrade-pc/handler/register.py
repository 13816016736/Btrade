# -*- coding: utf-8 -*-

from base import BaseHandler
from uimodule import geetest
import re, random, utils, config
from sendsms import *

#极验证
BASE_URL = "api.geetest.com/get.php?gt="
captcha_id = "9a601256e290cc2001027f5f701a48fb"
private_key = "c7ec51a45463e93b924f0ae462e0cdaa"
product = "embed"

class RegisterHandler(BaseHandler):
    def get(self):
        accept_purchaseinfo = self.db.query("select distinct purchaseinfoid from quote where state=1")
        accept_purchaseinfoids = []
        if accept_purchaseinfo:
            accept_purchaseinfoids = [str(item["purchaseinfoid"]) for item in accept_purchaseinfo]
        sum_quantity = 0
        sum_price = 0
        for item in accept_purchaseinfoids:
            purchaseinfo = self.db.get("select quantity,unit from purchase_info where id=%s", item)
            if purchaseinfo:
                quoteinfo = self.db.get(
                    "select price from quote where purchaseinfoid=%s and state=1 order by price desc limit 0,1", item)
                if purchaseinfo["unit"] == u"公斤":
                    sum_quantity += float(purchaseinfo["quantity"]) / 1000
                    sum_price += float(purchaseinfo["quantity"]) * float(quoteinfo["price"])

                elif purchaseinfo["unit"] == u"吨":
                    sum_quantity += float(purchaseinfo["quantity"])
                    sum_price += float(purchaseinfo["quantity"]) * float(quoteinfo["price"]) * 1000

        user_count = self.db.execute_rowcount("select id from users where type not in(1,2,9)")
        supplier_count = self.db.execute_rowcount("select id from supplier where pushstatus!=2")
        total = user_count + supplier_count

        totalquote = self.db.execute_rowcount("select id from quote")
        totalpurchaseinfo = self.db.execute_rowcount("select distinct purchaseinfoid from quote")
        averge_quote_num = 0
        if totalpurchaseinfo != 0:
            averge_quote_num = totalquote / totalpurchaseinfo

        #data = {"total": total, "accept_purchaseinfo_num": len(accept_purchaseinfo),"averge_quote_num": averge_quote_num, "sum_quantity": sum_quantity,"sum_price": int(sum_price / 10000)}
	    self.render("register_wx.html",total=total,accept_purchaseinfo_num=len(accept_purchaseinfo),
                    averge_quote_num=averge_quote_num,sum_quantity=int(sum_quantity),sum_price=int(sum_price / 10000)
                    )

    def post(self):
        pass

class CheckPhoneHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        phone = self.get_argument("phone")
        phonepattern = re.compile(r'^1(3[0-9]|4[57]|5[0-35-9]|8[0-9]|7[0-9])\d{8}$')
        phonematch = phonepattern.match(phone)
        if phonematch is False and phone is None:
            self.api_response({'status':'fail','message':'手机号填写错误'})
            return
        phonecount = self.db.execute_rowcount("select * from users where phone = %s", phone)
        if phonecount > 0:
            self.api_response({'status':'fail','message':'此手机号已被使用'})
            return
        smscode = self.get_argument("smscode")
        # challenge = self.get_argument("geetest_challenge")
        # validate = self.get_argument("geetest_validate")
        # seccode = self.get_argument("geetest_seccode")
        # gt = geetest.geetest(captcha_id, private_key)
        # result = gt.geetest_validate(challenge, validate, seccode)
        # if result and smscode == self.session.get("smscode"):
        #     self.session["phone"] = phone
        #     self.session.save()
        #     self.api_response({'status':'success','message':'验证成功','data':phone})
        # elif smscode != self.session.get("smscode"):
        #     self.api_response({'status':'fail','message':'短信验证码不正确','data':phone})
        # else:
        #     self.api_response({'status':'fail','message':'滑动验证码不正确'})
        if smscode == self.session.get("smscode"):
            self.session["phone"] = phone
            self.session.save()
            self.api_response({'status':'success','message':'验证成功','data':phone})
        else:
            self.api_response({'status':'fail','message':'短信验证码不正确','data':phone})

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
        message = utils.getSmsCode(phone, smscode)
        import json
        message = json.loads(message.encode("utf-8"))
        if message["result"]:
            self.session["smscode"] = smscode
            self.session.save()
            self.api_response({'status':'success','message':'短信验证码发送成功，请注意查收'})
        else:
            self.api_response({'status':'fail','message':'短信验证码发送失败，请稍后重试'})


class RegInfoHandler(BaseHandler):
    def get(self):
        if self.session.get("phone"):
            self.render("register_2.html", phone=self.session.get("phone"))
        else:
            self.redirect('/register')

    def post(self):
        username = self.get_argument("username")
        pattern = re.compile(r'^[A-Za-z0-9]{3,20}$')
        match = pattern.match(username)
        if match is False and username is None:
            self.api_response({'status':'fail','message':'会员名填写错误'})
            return
        usercount = self.db.execute_rowcount("select * from users where username = %s", username)
        if usercount > 0:
            self.api_response({'status':'fail','message':'此会员名已被使用'})
            return
        phone = self.session.get("phone")
        phonepattern = re.compile(r'^1(3[0-9]|4[57]|5[0-35-9]|8[0-9]|70)\d{8}$')
        phonematch = phonepattern.match(phone)
        if phonematch is False and phone is None:
            self.api_response({'status':'fail','message':'手机号填写错误'})
            return
        phonecount = self.db.execute_rowcount("select * from users where phone = %s", phone)
        if phonecount > 0:
            self.api_response({'status':'fail','message':'此手机号已被使用'})
            return
        password = self.get_argument("password")
        pwdRepeat = self.get_argument("pwdRepeat")
        if password is None and pwdRepeat is None and password != pwdRepeat:
            self.api_response({'status':'fail','message':'密码和确认密码填写错误'})
            return
        type = self.get_argument("type")
        if type is None:
            self.api_response({'status':'fail','message':'经营主体不能为空'})
            return
        name = self.get_argument("company",None) if type == u'7' else self.get_argument("name", None)
        if name is None:
            self.api_response({'status':'fail','message':'真实姓名或单位名称不能为空'})
            return
        nickname = self.get_argument("nickname")
        if nickname is None:
            self.api_response({'status':'fail','message':'个人称呼不能为空'})
            return

        lastrowid = self.db.execute_lastrowid("insert into users (username, password, phone, type, name, nickname, status, createtime)"
                             "value(%s, %s, %s, %s, %s, %s, %s, %s)", username, utils.md5(str(password + config.salt)), phone
                             , type, name, nickname, 1, int(time.time()))

        #查看是否为供应商列表里面的供应商，如果是转移积分
        supplier=self.db.query("select id,pushscore from supplier where mobile=%s",phone)
        if supplier:
            self.db.execute("update users set pushscore=%s where id=%s", supplier[0]["pushscore"],lastrowid)
            self.db.execute("update supplier set pushstatus=2 where id=%s", supplier[0]["id"])



        #因为去掉了user_info表,所以name字段直接放在users表了
        # result = self.db.execute("insert into user_info (userid, name)value(%s, %s)", lastrowid, name)
        self.session["userid"] = lastrowid
        self.session["user"] = username
        self.session.save()
        #发短信通知用户注册成功
        utils.regSuccessPc(phone, name, username)
        self.api_response({'status':'success','message':'注册成功','data':{'username':username}})

class RegResultHandler(BaseHandler):
    def get(self):
        self.render("register_3.html")

    def post(self):
        #供应商数量
        quoter = self.db.query("SELECT userid FROM `quote` group by userid")

        #采购商数量
        purchaser = self.db.query("SELECT userid FROM `purchase` group by userid")
        self.render("register_3.html", quoter=quoter, purchaser=purchaser)

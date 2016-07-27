# -*- coding: utf-8 -*-

from base import BaseHandler
import re,json,config,time,logging
from utils import *
import random
from webbasehandler import purchase_push_trace
import tornado.web

class RegisterHandler(BaseHandler):
    @purchase_push_trace
    def get(self, next_url="/"):
        userinfo = None
        code = self.get_argument("code", None)
        step= self.get_argument("step",'1')
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
        accept_purchaseinfo=self.db.query("select distinct purchaseinfoid from quote where state=1")
        accept_company_num=0
        accept_purchaseinfoids=[]
        if accept_purchaseinfo:
            accept_purchaseinfoids=[str(item["purchaseinfoid"]) for item in accept_purchaseinfo]
            accept_company_num=self.db.execute_rowcount("select distinct p.userid from purchase p left join  purchase_info pi on p.id=pi.purchaseid where pi.id in (%s)"%(",".join(accept_purchaseinfoids)))
        accept_quote_user_num=self.db.execute_rowcount("select distinct userid  from quote where state=1")
        accept_num = len(accept_purchaseinfoids)
        sum_quantity=0
        sum_price=0
        for item in accept_purchaseinfoids:
            purchaseinfo=self.db.get("select quantity,unit from purchase_info where id=%s",item)
            if purchaseinfo:
                quoteinfo=self.db.get("select price from quote where purchaseinfoid=%s and state=1 order by price desc limit 0,1",item)
                if purchaseinfo["unit"]==u"公斤":
                    sum_quantity+=int(purchaseinfo["quantity"])/1000
                    sum_price+=int(purchaseinfo["quantity"])*float(quoteinfo["price"])

                elif purchaseinfo["unit"]==u"吨":
                    sum_quantity += int(purchaseinfo["quantity"])
                    sum_price += int(purchaseinfo["quantity"]) * float(quoteinfo["price"])*1000
        show_data={"accept_company_num":accept_company_num,"accept_quote_user_num":accept_quote_user_num,
                   "accept_num":accept_num,"sum_quantity":sum_quantity,"sum_price":int(sum_price/10000)}






        self.render("register_%s.html"%step, next_url=next_url, userinfo=userinfo,data=show_data)

    @purchase_push_trace
    def post(self):
        step = self.get_argument("step", '1')
        print step
        if step=='1':
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
            openid=self.get_argument("openid","")
            self.session["phone"] = phone
            self.session["openid"] = openid
            self.session.save()
            print phone,openid
            self.api_response({'status': 'success', 'message': '验证成功'})
        elif step== '2':
            password = self.get_argument("password")
            if password=="":
                password = str(random.randint(100000, 999999))
            username = "ycg" + time.strftime("%y%m%d%H%M%S")
            type = self.get_argument("type")
            name = self.get_argument("name")
            if name is None:
                self.api_response({'status': 'fail', 'message': '真实姓名或单位名称不能为空'})
                return
            nickname = self.get_argument("nickname")
            if nickname is None and type!='8':
                self.api_response({'status': 'fail', 'message': '个人称呼不能为空'})
                return
            phone = self.session.get("phone")
            openid= self.session.get("openid")
            if phone or openid:
                self.session["phone"] = ""
                self.session["openid"] = ""
                self.session.save()
                lastrowid = self.db.execute_lastrowid(
                        "insert into users (username, password, phone, type, name, nickname, status, openid,createtime)"
                        "value(%s, %s, %s, %s, %s, %s, %s, %s, %s)", username, md5(str(password + config.salt)), phone
                        , type, name, nickname, 1, openid, int(time.time()))
                # 查看是否为供应商列表里面的供应商，如果是转移积分
                supplier = self.db.query("select id,pushscore from supplier where mobile=%s", phone)
                if supplier:
                    self.db.execute("update users set pushscore=%s where id=%s", supplier[0]["pushscore"], lastrowid)
                    self.db.execute("update supplier set pushstatus=2 where id=%s", supplier[0]["id"])

                notification = self.db.query("select id from notification where receiver = %s", lastrowid)
                self.session["userid"] = lastrowid
                self.session["user"] = username
                self.session["notification"] = len(notification)
                self.session.save()
                # 发短信通知用户注册成功
                #regSuccess(phone, name, username)
                # 发微信模板消息通知用户注册成功
                #regSuccessWx(openid, name, username)
                self.api_response({'status': 'success', 'message': '注册成功'})
            else:
                self.api_response({'status': 'fail', 'message': 'session过期'})
                return
        elif step=='3':
            attention=self.get_argument("attention")
            self.db.execute("update users set varietyids=%s where id=%s",attention,self.session.get("userid"))
            self.api_response({'status': 'success', 'data': {}})











class GetSmsCodeHandler(BaseHandler):
    def get(self):
        pass

    @purchase_push_trace
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
        print smscode
        #message = getSmsCode(phone, smscode)
        message={}
        message["result"]="11"
        #message = json.loads(message.encode("utf-8"))
        if message["result"]:
            self.session["smscode"] = smscode
            self.session.save()
            self.api_response({'status':'success','message':'短信验证码发送成功，请注意查收'})
        else:
            self.api_response({'status':'fail','message':'短信验证码发送失败，请稍后重试'})

class RegSuccessHandler(BaseHandler):
    def get(self):
        next_url=self.get_argument("next_url", "/")
        browser_type=self.get_argument("browser_type","wx")
        if next_url.find("/quote/purchaseinfoid/")==0:
            self.render("register_A.html",type=1,url=next_url,username=self.session.get("user"))
        else:
            if browser_type=="wx":
                self.redirect("https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx90e04052c49aa63e&redirect_uri=http://m.yaocai.pro/checkfans&response_type=code&scope=snsapi_base&state=regsuccess#wechat_redirect")
            else:
                self.render("register_C.html")

    @purchase_push_trace
    def post(self):
        self.render("register_result.html" ,next_url=self.get_argument("next_url", "/"))
class CheckFansHandler(BaseHandler):
    def get(self):
        is_fans=False
        code = self.get_argument("code", None)
        state = self.get_argument("state",None)
        if code:
            # 请求获取access_token和openid
            url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (
            config.appid, config.secret, code)
            res = requests.get(url)
            message = json.loads(res.text.encode("utf-8"))
            access_token = message.get("access_token", None)
            if access_token:
                openid = message.get("openid")
                # 请求获取用户信息
                url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN" % (access_token, openid)
                res = requests.get(url)
                userinfo = json.loads(res.text.encode("utf-8"))
                subscribe=userinfo.get("subscribe")
                if subscribe==1:
                    is_fans=True
                else:
                    is_fans = False
        if is_fans:
            if state == "regsuccess":
                self.render("register_A.html", type=2, url="/", username=self.session.get("user"))
            elif state =="quotesuccess":
                self.render("quote_success_A.html")
        else:
            if state == "regsuccess":
                self.render("register_B.html")
            elif state =="quotesuccess":
                self.render("quote_success_B.html")
        self.redirect("/")

class VarietySearchHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        varietyName=self.get_argument("key",None)
        print varietyName
        if varietyName:
            varieties=self.db.query("select id,name from variety where name like '%%%%%s%%%%' or find_in_set('%s',alias)" %(varietyName,varietyName))
            if len(varieties)!=0:
                self.api_response({"status": "success", "list": varieties})
            else:
                self.api_response({"status": "notsupport", "msg":""})
        else:
            self.api_response({"status": "fail","msg":""})
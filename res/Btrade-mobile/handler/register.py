# -*- coding: utf-8 -*-

from base import BaseHandler
import re,json,config,time,logging
from utils import *
import random
from webbasehandler import purchase_push_trace
import tornado.web
from wechatjsapi import *

class RegisterHandler(BaseHandler):
    @purchase_push_trace
    def get(self, next_url="/"):
        userinfo = None
        code = self.get_argument("code", None)
        step= self.get_argument("step",'1')
        registertype=self.get_argument("register",'1')
        if code:
            #请求获取access_token和openid
            appid = config.appid
            secret = config.secret
            if int(registertype)==2:
                appid = config.purchase_appid
                secret = config.purchase_secret
            url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code" % (appid, secret, code)
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
        show_data={}
        attentionvariety = []
        if step=="1":
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

            if int(registertype)==2:
                user_count = self.db.execute_rowcount("select id from users where type not in(1,2,9)")
                supplier_count = self.db.execute_rowcount("select id from supplier where pushstatus!=2")
                total = user_count + supplier_count

                totalquote=self.db.execute_rowcount("select id from quote")
                totalpurchaseinfo=self.db.execute_rowcount("select distinct purchaseinfoid from quote")
                averge_quote_num=0
                if totalpurchaseinfo!=0:
                    averge_quote_num=totalquote/totalpurchaseinfo


                show_data = {"total": total, "accept_purchaseinfo_num": len(accept_purchaseinfo),
                             "averge_quote_num": averge_quote_num, "sum_quantity": sum_quantity,
                             "sum_price": int(sum_price / 10000)}
            else:
                show_data={"accept_company_num":accept_company_num,"accept_quote_user_num":accept_quote_user_num,
                   "accept_num":accept_num,"sum_quantity":sum_quantity,"sum_price":int(sum_price/10000)}
        elif step=="3":
            if int(registertype)==2:
                self.redirect("/regsuccess?next_url=%s"%next_url)
                return
            attention=[]
            if next_url!="/":
                url_split=next_url.split("/")
                if len(url_split)>=4:
                    purchaseinfoid=url_split[3]
                    varity=self.db.get("select varietyid from purchase_info where id=%s", purchaseinfoid)
                    if varity:
                        attention.append(varity["varietyid"])

            user=self.db.get("select phone from users where id=%s",self.session.get("userid"))
            if user:
                phone=user["phone"]
                supplier=self.db.query("select variety from supplier where mobile=%s",phone)
                if len(supplier)!=0:
                     supplier_varitey=supplier[0]["variety"].split(",")
                     attention[1:1] = supplier_varitey

            if len(attention)!=0:
                attention=[str(item) for item in attention]
                attention=list(set(attention))#去重
                attentionvariety = self.db.query(
                        "select id,name from variety where id in(%s)" % ",".join(attention))

        self.render("register_%s.html"%step, next_url=next_url, userinfo=userinfo,data=show_data,attention=attentionvariety,register=int(registertype))

    @purchase_push_trace
    def post(self):
        step = self.get_argument("step", '1')
        #print step
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
            city=self.get_argument("city","")
            self.session["phone"] = phone
            self.session["openid"] = openid
            self.session["city"] = city
            self.session.save()
            #print phone,openid
            self.api_response({'status': 'success', 'message': '验证成功'})
        elif step== '2':
            password = self.get_argument("password")
            if password=="":
                password = str(random.randint(100000, 999999))
            username = "ycg" + time.strftime("%y%m%d%H%M%S")
            type = self.get_argument("type")
            name = self.get_argument("name")
            registertype=self.get_argument("registertype",1)
            if name is None:
                self.api_response({'status': 'fail', 'message': '真实姓名或单位名称不能为空'})
                return
            nickname = self.get_argument("nickname")
            if nickname is None and type!='8':
                self.api_response({'status': 'fail', 'message': '个人称呼不能为空'})
                return
            phone = self.session.get("phone")
            openid= self.session.get("openid")
            city=self.session.get("city")
            areaid=0
            if city:
                logging.info(city)
                try:
                    areaid=self.db.get("select id from where areaname=%s or shortname=%s ",city.encode("utf8").decode("GBK"),city.encode("utf8").decode("GBK"))
                except Exception,ex:
                    logging.info("get city ex=%s",str(ex))

            if phone or openid:
                self.session["phone"] = ""
                self.session["openid"] = ""
                self.session.save()
                if int(registertype)==1:
                    lastrowid = self.db.execute_lastrowid(
                        "insert into users (username, password, phone, type, name, nickname,areaid, status, openid,registertype,createtime)"
                        "value(%s, %s, %s, %s,%s, %s, %s, %s, %s, %s,%s)", username, md5(str(password + config.salt)), phone
                        , type, name, nickname,areaid, 1, openid,registertype, int(time.time()))
                else:
                    lastrowid = self.db.execute_lastrowid(
                        "insert into users (username, password, phone, type, name, nickname,areaid, status, openid2,registertype,createtime)"
                        "value(%s, %s, %s, %s,%s, %s, %s, %s, %s, %s,%s)", username, md5(str(password + config.salt)), phone
                        , type, name, nickname,areaid, 1, openid,registertype, int(time.time()))
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
                #regSuccess(phone, name, username,int(registertype))
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
        message={}
        message["result"]="112"
        #message = getSmsCode(phone, smscode)
        #message = json.loads(message.encode("utf-8"))
        if message["result"]:
            self.session["smscode"] = smscode
            self.session.save()
            self.api_response({'status':'success','message':'短信验证码发送成功，请注意查收'})
        else:
            self.api_response({'status':'fail','message':'短信验证码发送失败，请稍后重试'})

class RegSuccessHandler(BaseHandler):
    @purchase_push_trace
    def get(self):
        next_url=self.get_argument("next_url", "/")
        purchaseinfonum=self.db.execute_rowcount("select id from purchase_info where status!=0")
        if next_url.find("/quote/purchaseinfoid/")==0:
            self.render("register_A.html",type=1,url=next_url,username=self.session.get("user"),purchaseinfonum=purchaseinfonum)
        else:
            ua = self.request.headers['User-Agent']
            if ua.lower().find("micromessenger") != -1:
                self.redirect("/checkfans?state=regsuccess")
            else:
                self.render("register_C.html",purchaseinfonum=purchaseinfonum)

    @purchase_push_trace
    def post(self):
        self.render("register_result.html" ,next_url=self.get_argument("next_url", "/"))
class CheckFansHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        is_fans=False
        state= self.get_argument("state",None)
        pid= self.get_argument("pid", "")
        ret=self.db.get("select openid,name,username,registertype,openid2 from users where id=%s",self.session.get("userid"))
        name=ret["name"]
        username=ret["username"]
        openid=ret["openid"]
        registertype=ret["registertype"]
        if int(registertype)==2 or state=="purchasesuccess":
            openid=ret["openid2"]
            registertype=2
        purchaseinfonum = self.db.execute_rowcount("select id from purchase_info where status!=0")
        if openid!="":
            openid = openid .strip("\r\n")
            # 请求获取access_token和openid
            wechart = WechartJSAPI(self.db)
            access_token = wechart.getAccessToken(int(registertype))
            if access_token:
                # 请求获取用户信息
                url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN" % (access_token, openid)
                res = requests.get(url)
                data = json.loads(res.text.encode("utf-8"))
                logging.info(data)
                errorCode=data.get("errcode",None)
                if errorCode:
                    access_token = wechart.getRefeshAccessToken(int(registertype))
                    url = "https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s&lang=zh_CN" % (
                    access_token, openid)
                    res = requests.get(url)
                    data = json.loads(res.text.encode("utf-8"))
                    logging.info(data)
                subscribe=data.get("subscribe",0)
                if subscribe==1:
                    is_fans=True
                else:
                    is_fans = False
        if is_fans:
            if state == "regsuccess":
                # 发微信模板消息通知用户注册成功
                regSuccessWx(openid, name, username,int(registertype))
                if registertype==1:
                    self.render("register_A.html", type=2, url="/", username=self.session.get("user"),purchaseinfonum=purchaseinfonum,registertype=registertype)
                else:
                    user_count = self.db.execute_rowcount("select id from users where type not in(1,2,9)")
                    supplier_count = self.db.execute_rowcount("select id from supplier where pushstatus!=2")
                    total = user_count + supplier_count

                    purchase_user = self.db.execute_rowcount(
                        "select distinct p.userid from purchase p left join  purchase_info pi on p.id=pi.purchaseid ")

                    accept_quote = self.db.execute_rowcount("select id from quote where state=1")

                    self.render("register_A.html", type=2, url="/", username=self.session.get("user"),
                                purchaseinfonum=purchaseinfonum,total=total,purchase_user=purchase_user,accept_quote=accept_quote,registertype=registertype)
            elif state =="quotesuccess":
                self.render("quote_success_A.html",purchaseinfonum=purchaseinfonum)
            elif state =="purchasesuccess":
                supplier_num=100
                variety=""
                purchaseinfo=self.db.get("select varietyid,name from purchase_info where id=%s",pid)
                if purchaseinfo:
                    variety=purchaseinfo["name"]
                    user_count = self.db.execute_rowcount("select id from users where type not in(1,2,9) and find_in_set(%s,varietyids)",purchaseinfo["varietyid"])
                    supplier_count = self.db.execute_rowcount("select id from supplier where pushstatus!=2 and  find_in_set(%s,variety)",purchaseinfo["varietyid"])
                    supplier_num = user_count + supplier_count
                self.render("purchase_success_A.html",supplier_num=supplier_num,variety=variety,pid=pid)
            else:
                self.redirect("/")
        else:
            if state == "regsuccess":
                self.render("register_B.html",purchaseinfonum=purchaseinfonum,registertype=registertype)
            elif state =="quotesuccess":
                self.render("quote_success_B.html",purchaseinfonum=purchaseinfonum)
            elif state =="purchasesuccess":
                user_count = self.db.execute_rowcount("select id from users where type not in(1,2,9)")
                supplier_count = self.db.execute_rowcount("select id from supplier where pushstatus!=2")
                total = user_count + supplier_count

                self.render("purchase_success_B.html",total=total)
            else:
                self.redirect("/")

class VarietySearchHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        varietyName=self.get_argument("key",None)
        #print varietyName
        if varietyName:
            varieties=self.db.query("select id,name from variety where name like %s or alias like %s" ,"%"+varietyName+"%", "%"+varietyName+"%",)
            if len(varieties)!=0:
                self.api_response({"status": "success", "list": varieties})
            else:
                self.api_response({"status": "notsupport", "msg":""})
        else:
            self.api_response({"status": "fail","msg":""})

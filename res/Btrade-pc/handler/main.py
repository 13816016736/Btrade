# -*- coding: utf-8 -*-

from base import BaseHandler
from collections import defaultdict
# from config import *
import os,config,logging,utils,re,random

class MainHandler(BaseHandler):
    def get(self):
        #最新采购单
        purchases = self.db.query("select p.id,p.createtime,u.name,u.type from purchase p left join users u on p.userid = u.id where p.status != 0 order by p.createtime desc limit 5")
        purchaseids = [str(purchase["id"]) for purchase in purchases]
        purchaseinf = defaultdict(list)
        if purchaseids:
            purchaseinfos = self.db.query("select id,purchaseid,name,specification,origin,quantity,quality,unit from purchase_info where purchaseid in (%s)"%",".join(purchaseids))
            purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
            purchaseattachments = self.db.query("select * from purchase_attachment where purchase_infoid in (%s)"%",".join(purchaseinfoids))
            attachments = defaultdict(list)
            for attachment in purchaseattachments:
                attachments[attachment["purchase_infoid"]] = attachment
            purchaseinf = defaultdict(list)
            for purchaseinfo in purchaseinfos:
                purchaseinfo["attachments"] = attachments.get(purchaseinfo["id"])
                purchaseinf[purchaseinfo["purchaseid"]].append(purchaseinfo)
        for purchase in purchases:
            purchase["purchaseinfo"] = purchaseinf.get(purchase["id"])
            purchase["variety"] = len(purchase["purchaseinfo"]) if purchase["purchaseinfo"] else 0

        #最新报价
        #quotes = self.db.query("select ta.*,u.name pname from (select t.*,u.name qname from (select qp.*,p.userid puid from "
        #"(select q.id,q.userid quid,q.quality,q.price,q.createtime,pi.id pid,pi.purchaseid,pi.name,pi.specification,pi.unit "
        #"from quote q,purchase_info pi where q.purchaseinfoid = pi.id order by q.createtime desc limit 4)"
        #" qp left join purchase p on qp.purchaseid = p.id) t left join users u on t.quid = u.id) ta left join users u on ta.puid = u.id")

        quotes =self.db.query("select q.id,q.userid quid,q.quality,q.price,q.createtime,pi.id pid,pi.purchaseid,pi.name,pi.specification,pi.unit from "
        "quote q,purchase_info pi where q.purchaseinfoid = pi.id order by q.createtime desc limit 4")#获取最新的4个报价
        purchaseids = [str(quote["purchaseid"]) for quote in quotes]#采购单id list
        if len(purchaseids)!=0:
            purchaseuser = self.db.query(
            "select p.id,name from purchase p left join users u on p.userid=u.id where p.id in(%s)" % ",".join(
                purchaseids))
            purchaseuserinfo = dict((i.id, i.name) for i in  purchaseuser)
            for quote in quotes :
                quote["pname"]=purchaseuserinfo[quote.purchaseid]



        quoteids = [str(quote["id"]) for quote in quotes]
        #取报价图片
        if quoteids:
            quoteattachments = self.db.query("select * from quote_attachment where quoteid in (" + ",".join(quoteids) + ")")
            myquoteattachments = {}
            for quoteattachment in quoteattachments:
                base, ext = os.path.splitext(os.path.basename(quoteattachment["attachment"]))
                quoteattachment["attachment"] = config.img_domain+quoteattachment["attachment"][quoteattachment["attachment"].find("static"):].replace(base, base+"_thumb")
                if myquoteattachments.has_key(quoteattachment["quoteid"]):
                    myquoteattachments[quoteattachment["quoteid"]].append(quoteattachment["attachment"])
                else:
                    myquoteattachments[quoteattachment["quoteid"]] = [quoteattachment["attachment"]]
        for mq in quotes:
            if myquoteattachments.has_key(mq.id):
                mq["attachments"] = myquoteattachments[mq.id]
            else:
                mq["attachments"] = []
        #采购批次总数和报价总数
        pvariety = self.db.execute_rowcount("select id from purchase_info")
        qcount = self.db.execute_rowcount("select q.id from quote q,purchase_info pi where q.purchaseinfoid = pi.id")
        self.render("index.html", purchases=purchases, quotes=quotes, pvariety=pvariety, qcount=qcount)

class ContactHandler(BaseHandler):
    def get(self):
        self.render("contact.html")

class AboutusHandler(BaseHandler):
    def get(self):
        self.render("aboutus.html")

class QuoteHandler(BaseHandler):
    def get(self):
        self.render("quote.html")

class ForgetPwdHandler(BaseHandler):
    def get(self):
        self.render("update_password.html")

    def post(self):
        smscode = self.get_argument("smscode")
        phone = self.get_argument("phone")
        if self.db.get("select * from users where phone = %s" , phone):
            # 验证手机验证码
            if self.session.get("smscode") == smscode:
                self.session["phone"] = phone
                self.session.save()
                self.render("update_password_2.html", smscode=smscode)
            else:
                self.error("手机验证码错误","/forgetpwd")
        else:
            self.error("手机号不存在","/forgetpwd")

class SetPwdHandler(BaseHandler):

    def post(self):
        smscode = self.get_argument("smscode")
        password = self.get_argument("password")
        repassword = self.get_argument("repassword")
        phone = self.session.get("phone")
        if password is None and repassword is None and password <> repassword:
            self.error("密码和确认密码填写错误","/forgetpwd")
        user = self.db.get("select id from users where phone = %s", phone)
        if len(user) == 1:
            # 验证手机验证码
            if self.session.get("smscode") == smscode:
                self.db.update("update users set password = %s where id = %s", utils.md5(str(password + config.salt)), user["id"])
                self.success("操作成功","/")
            else:
                self.error("手机验证码错误","/forgetpwd")
        else:
            self.error("手机号存在异常，请联系客服人员","/forgetpwd")

class GetSmsCodeForPwdHandler(BaseHandler):

    def post(self):
        phone = self.get_argument("phone")
        phonepattern = re.compile(r'^1(3[0-9]|4[57]|5[0-35-9]|8[0-9]|7[0-9])\d{8}$')
        phonematch = phonepattern.match(phone)
        if phonematch is None:
            self.api_response({'status':'fail','message':'手机号填写错误'})
            return
        phonecount = self.db.execute_rowcount("select * from users where phone = %s", phone)
        if phonecount == 0:
            self.api_response({'status':'fail','message':'此手机号暂未注册'})
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

# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import json, os, datetime
from utils import *
from config import *
import random
import time
from collections import defaultdict
from webbasehandler import purchase_push_trace

class QuoteHandler(BaseHandler):

    @purchase_push_trace
    @tornado.web.authenticated
    def get(self, purchaseinfoid):
        #purchaseinfo = self.db.get("select t.*,a.position from (select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,"
        #"p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.term,p.status,p.areaid,p.invoice,pi.id pid,"
        #"pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specification,pi.views from purchase p,purchase_info pi "
        #"where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid", purchaseinfoid)
        #获取采购单信息
        purchaseinfo = self.db.get(
            "select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,"
            "p.term,p.status,p.areaid,p.invoice,pi.id pid,pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specification,"
            "pi.views from purchase p,purchase_info pi where p.id = pi.purchaseid and pi.id = %s", purchaseinfoid)

        # 获取采购单area信息
        areaid = purchaseinfo["areaid"]
        areainfo = self.db.get("select position from area where id =%s", areaid)
        if areainfo:
            purchaseinfo["position"] = areainfo.position
        else:
            purchaseinfo["position"] =""


            #获得采购品种图片
        attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", purchaseinfoid)
        for attachment in attachments:
            base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
            attachment["attachment"] = config.img_domain+attachment["attachment"][attachment["attachment"].find("static"):].replace(base, base+"_thumb")
        purchaser = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
        purchaseinfo["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(purchaseinfo["createtime"])))
        if purchaseinfo["term"] != 0:
            purchaseinfo["expire"] = datetime.datetime.fromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
            purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
        purchaseinfo["attachments"] = attachments

        #此采购商成功采购单数
        purchases = self.db.execute_rowcount("select * from purchase where userid = %s and status = 4", purchaser["id"])
        #此采购单报价数
        quotes = self.db.execute_rowcount("select * from quote where purchaseinfoid = %s", purchaseinfoid)
        #此采购商回复供应商比例
        purchaser_quotes = self.db.query("select p.id,p.userid,t.state state from purchase p left join "
            "(select pi.purchaseid,q.state from purchase_info pi left join quote q on pi.id = q.purchaseinfoid) t "
                "on p.id = t.purchaseid where p.userid = %s", purchaser["id"])
        reply = 0
        print purchaser_quotes
        for purchaser_quote in purchaser_quotes:
            if purchaser_quote.state is not None and purchaser_quote.state != 0:
                reply = reply + 1

        #本周可报价次数
        t = time.time()
        week_begin = get_week_begin(t,0)
        week_end = get_week_begin(t,1)
        quotecount = self.db.execute_rowcount("select id from quote where userid = %s and createtime > %s and createtime < %s"
                                 , self.session.get("userid"), week_begin,week_end)
        quotechances = config.conf['QUOTE_NUM'] - quotecount if config.conf['QUOTE_NUM'] - quotecount > 0 else 0

        #获取图片
        uploadfiles = self.session.get("uploadfiles_quote", {})
        for k in uploadfiles:
            base, ext = os.path.splitext(os.path.basename(uploadfiles[k]))
            uploadfiles[k] = config.img_domain+uploadfiles[k][uploadfiles[k].find("static"):].replace(base, base+"_thumb")
        self.render("quote.html", purchaser=purchaser, purchase=purchaseinfo, purchases=purchases, quotes=quotes,
                    reply=int((float(reply)/float(len(purchaser_quotes))*100) if len(purchaser_quotes) != 0 else 0),
                    uploadfiles=uploadfiles, quotechances=quotechances)

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        purchaseinfoid = self.get_argument("purchaseinfoid")
        #验证对X采购单报价
        if purchaseinfoid == "":
            self.api_response({'status':'fail','message':'请选择采购单进行报价'})
            return
        quality = self.get_argument("quality")
        price = self.get_argument("price")
        #验证表单信息,货源描述,价格,价格说明
        if quality == "" or price == "":
            self.api_response({'status':'fail','message':'请完整填写'})
            return
        #至少上传一张图片
        uploadfiles = self.session.get("uploadfiles_quote")
        if len(uploadfiles) == 0:
            self.api_response({'status':'fail','message':'至少上传一张图片'})
            return
        #本周可报价次数
        t = time.time()
        week_begin = get_week_begin(t,0)
        week_end = get_week_begin(t,1)
        quotecount = self.db.execute_rowcount("select id from quote where userid = %s and createtime > %s and createtime < %s"
                                 , self.session.get("userid"), week_begin,week_end)
        if config.conf['QUOTE_NUM'] - quotecount < 0:
            self.api_response({'status':'fail','message':'本周已用完5次报价机会,无法再进行报价'})
            return
        #一个用户只能对同一个采购单报价一次
        quote = self.db.get("select id from quote where userid = %s and purchaseinfoid = %s and state = 0", self.session.get("userid"), purchaseinfoid)
        if quote is not None:
            self.api_response({'status':'fail','message':'您已经对次采购单进行过报价,无法再次报价'})
            return
        #不能对自己的采购单进行报价
        purchase = self.db.get("select t.*,u.name uname,u.phone,u.openid from (select p.userid,p.term,p.createtime,pi.name,pi.specification,pi.quantity,pi.unit from purchase_info pi,purchase p where p.id = pi.purchaseid and pi.id = %s) "
                               "t left join users u on u.id = t.userid", purchaseinfoid)
        if purchase["userid"] == self.session.get("userid"):
            self.api_response({'status':'fail','message':'不能对自己的采购单进行报价'})
            return
        #报价结束不能报价
        if purchase["term"] != 0:
            purchase["expire"] = datetime.datetime.fromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
            if (purchase["expire"] - datetime.datetime.now()).days <= 0:
                self.api_response({'status':'fail','message':'此采购单报价已结束，无法再进行报价'})
                return

        today = time.time()
        quoteid = self.db.execute_lastrowid("insert into quote(userid,purchaseinfoid,quality,price,`explain`,createtime)value"
                                            "(%s,%s,%s,%s,%s,%s)", self.session.get("userid"),self.get_argument("purchaseinfoid"),
                                            quality,price,self.get_argument("explain"),
                                            int(today))

        #保存session上传图片的路径
        if uploadfiles:
            for key in uploadfiles:
                self.db.execute("insert into quote_attachment (quoteid, attachment, type)value(%s, %s, %s)", quoteid, uploadfiles[key], key)
            uploadfiles = {}
            self.session["uploadfiles_quote"] = uploadfiles
            self.session.save()

        #给采购商发送通知
        #获得采购商userid
        quoter = self.db.get("select name,phone,openid from users where id = %s", self.session.get("userid"))
        title = quoter["name"].encode('utf-8') + "对【" + purchase["name"].encode('utf-8') + "】提交了报价，立即处理"

        self.db.execute("insert into notification(sender,receiver,type,title,content,status,createtime)value(%s, %s, %s, %s, %s, %s, %s)",
                        self.session.get("userid"),purchase["userid"],2,title,self.get_argument("purchaseinfoid"),0,int(time.time()))

        #发短信通知采购商有用户报价
        quoteSms(purchase["phone"], purchase["name"], quoter["name"], price, config.unit)
        #发微信模板消息通知采购商有用户报价
        quoteWx(purchase["openid"], purchaseinfoid, purchase["name"], quoter["name"], price, purchase["unit"], quality, today)
        #发微信模板消息提示报价的供应商报价成功啦
        quoteSuccessWx(quoter["openid"], purchase["uname"], purchase["name"], purchase["specification"], purchase["quantity"], price, purchase["unit"], quality, today)
        self.api_response({'status':'success','message':'请求成功'})

class QuoteUploadHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self, purchaseinfoid, type):
        print purchaseinfoid
        print type
        self.render("uploads_pic.html", purchaseinfoid=purchaseinfoid, type=type)

    @tornado.web.authenticated
    def post(self):
        pass

class QuoteSuccessHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        pass

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        if self.session.get("uploadfiles_quote"):
            self.session["uploadfiles_quote"] = {}
            self.session.save()
        first = False
        purchaseinfoid = self.get_argument("purchaseinfoid", None)
        if purchaseinfoid:
            count = self.db.execute_rowcount("select id from quote where purchaseinfoid = %s", purchaseinfoid)
            if count == 1:
                first = True
        self.render("quote_success.html", first=first)


class WeixinHandler(BaseHandler):

    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        self.render("weixin.html")

    @tornado.web.authenticated
    def post(self):
        pass

class QuoteDetailHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self, quoteid, nid):
        quote = self.db.get("select * from quote where id = %s", quoteid)
        quote["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(quote["createtime"])))
        quoteattachment = self.db.query("select * from quote_attachment where quoteid = %s", quoteid)
        for qa in quoteattachment:
            base, ext = os.path.splitext(os.path.basename(qa["attachment"]))
            qa["attachment"] = config.img_domain+qa["attachment"][qa["attachment"].find("static"):].replace(base, base+"_thumb")

        #查询采购单信息
        #purchaseinfo = self.db.get("select t.*,a.position from "
        #"(select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.term,p.status,p.areaid,p.invoice,pi.id pid,"
        #"pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specification,pi.views from purchase p,purchase_info pi "
        #"where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid", quote["purchaseinfoid"])

        # 获取采购单信息
        purchaseinfo = self.db.get(
            "select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,"
            "p.term,p.status,p.areaid,p.invoice,pi.id pid,pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specification,"
            "pi.views from purchase p,purchase_info pi where p.id = pi.purchaseid and pi.id = %s", quote["purchaseinfoid"])

        # 获取采购单area信息
        areaid = purchaseinfo["areaid"]
        areainfo = self.db.get("select position from area where id =%s", areaid)
        if areainfo:
            purchaseinfo["position"] = areainfo.position
        else:
            purchaseinfo["position"]=""




        quote["unit"] = purchaseinfo["unit"]

        #获得采购品种图片
        attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", quote["purchaseinfoid"])
        for attachment in attachments:
            base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
            attachment["attachment"] = config.img_domain+attachment["attachment"][attachment["attachment"].find("static"):].replace(base, base+"_thumb")
        user = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
        purchaseinfo["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(purchaseinfo["createtime"])))
        if purchaseinfo["term"] != 0:
            purchaseinfo["expire"] = datetime.datetime.fromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
            purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
        purchaseinfo["attachments"] = attachments

        others = self.db.query("select id from purchase_info where purchaseid = %s and id != %s",
                                      purchaseinfo["id"], purchaseinfo["pid"])

        #此采购商成功采购单数
        purchases = self.db.execute_rowcount("select * from purchase where userid = %s and status = 4", user["id"])
        #此采购单报价数
        quotes = self.db.query("select * from quote where purchaseinfoid = %s", purchaseinfo["pid"])
        acceptuserid = []
        for q in quotes:
            if q.state == 1:
                acceptuserid.append(str(q.userid))
        acceptuser = []
        if acceptuserid:
            acceptuser = self.db.query("select nickname from users where id in (" + ",".join(acceptuserid) + ")")
        #此采购商回复供应商比例
        purchaser_quotes = self.db.query("select p.id,p.userid,t.state state from purchase p left join "
            "(select pi.purchaseid,q.state from purchase_info pi left join quote q on pi.id = q.purchaseinfoid) t "
                "on p.id = t.purchaseid where p.userid = %s", user["id"])
        reply = 0

        for purchaser_quote in purchaser_quotes:
            if purchaser_quote.state is not None and purchaser_quote.state != 0:
                reply = reply + 1

        #报价回复消息标记为已读
        if int(nid) > 0:
            self.db.execute("update notification set status = 1 where receiver = %s and id = %s", self.session.get("userid"), nid)

        self.render("quote_detail.html", user=user, purchase=purchaseinfo, others=len(others), purchases=purchases,
                    quotes=quotes, acceptuser=acceptuser, reply=int((float(reply)/float(len(purchaser_quotes))*100) if len(purchaser_quotes) != 0 else 0),
                    quote=quote, quoteattachment=quoteattachment)

    @tornado.web.authenticated
    def post(self):
        pass

class QuoteListHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        #获取我发出的报价信息
        #myquotes = self.db.query("select ta.*,n.id nid from (select mq.*,u.name uname,u.nickname,u.type,u.phone from "
        #                         "(select ta.*,p.createtime purchasetime,p.term,p.userid purchaseuserid from ("
        #                         "select q.*,pi.purchaseid,pi.name,pi.specification,pi.origin,pi.quantity,pi.unit "
        #                         "from quote q,purchase_info pi where q.purchaseinfoid = pi.id and q.userid = %s order by q.createtime desc"
        #                         ") ta,purchase p where ta.purchaseid = p.id) mq,users u where mq.purchaseuserid = u.id) ta "
        #                         "left join notification n on ta.userid = n.sender and n.content = ta.purchaseinfoid", userid)
        myquotes = self.db.query("select q.*,pi.purchaseid,pi.name,pi.specification,pi.origin,pi.quantity,pi.unit "
                                 "from quote q,purchase_info pi where q.purchaseinfoid = pi.id and q.userid = %s order by q.createtime desc",userid)#获取我的报价信息
        if myquotes:
            purchaseids= [str(quote["purchaseid"]) for quote in myquotes]
            purchaseinfoids=[str(quote["purchaseinfoid"]) for quote in myquotes]
            purchase =self.db.query("select id,createtime purchasetime,term,userid purchaseuserid from purchase where id in(%s)" %",".join(purchaseids))#获取报价的采购单信息
            purchasedict = dict((i.id, [i.purchasetime,i.term,i.purchaseuserid]) for i in purchase)
            userinfo = self.db.get(
                "select id,nickname,name,type,phone from users where id =%s ",userid)  # 获取user信息
            notification=self.db.query("select content as purchaseinfoid, id from notification where sender=%s and content in(%s)"%(userid,",".join(purchaseinfoids)))#获取该user的notification
            notificationdict = dict((i.purchaseinfoid, i.id) for i in notification)




        quoteids = []
        over = 0
        unreply = 0
        for myquote in myquotes:
            #拼接信息
            myquote["purchasetime"]=purchasedict[myquote["purchaseid"]][0]
            myquote["term"]=purchasedict[myquote["purchaseid"]][1]
            myquote["purchaseuserid"] = purchasedict[myquote["purchaseid"]][2]
            myquote["nickname"]=userinfo["nickname"]
            myquote["uname"] = userinfo["name"]
            myquote["type"]=userinfo["type"]
            myquote["phone"] = userinfo["phone"]
            myquote["nid"]= notificationdict[str(myquote.purchaseinfoid)]



            quoteids.append(str(myquote.id))
            expire = datetime.datetime.fromtimestamp(float(myquote["purchasetime"])) + datetime.timedelta(myquote["term"])
            myquote["timedelta"] = (expire - datetime.datetime.now()).days
            myquote["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(myquote["createtime"])))
            if myquote["timedelta"] <= 0:
                over =+ 1
            if myquote.state == 0:
                unreply =+ 1

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
        for mq in myquotes:
            if myquoteattachments.has_key(mq.id):
                mq["attachments"] = myquoteattachments[mq.id]
            else:
                mq["attachments"] = []

        self.render("quote_list.html", myquotes=myquotes, over=over, unreply=unreply)

    @tornado.web.authenticated
    def post(self):
        pass
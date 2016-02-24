# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import json, os, datetime
from utils import *
from config import *
import random
import time
from collections import defaultdict

class QuoteHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, purchaseinfoid):
        purchaseinfo = self.db.get("select n.*,sp.specification from (select t.*,a.areaname from "
        "(select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.limited,p.term,p.status,p.areaid,p.invoice,pi.id pid,"
        "pi.name,pi.price,pi.quantity,pi.quality,pi.origin,pi.specificationid,pi.views from purchase p,purchase_info pi left join specification s on s.id = pi.specificationid "
        "where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid) n left join "
        "specification sp on n.specificationid = sp.id",
                                     purchaseinfoid)

        #获得采购品种图片
        attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", id)
        for attachment in attachments:
            base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
            attachment["attachment"] = config.img_domain+attachment["attachment"][attachment["attachment"].find("static"):].replace(base, base+"_thumb")
        purchaser = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
        purchaseinfo["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(purchaseinfo["createtime"])))
        if purchaseinfo["limited"] == 1:
            purchaseinfo["expire"] = datetime.datetime.utcfromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
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
        uploadfiles = self.session.get("uploadfiles", {})
        for k in uploadfiles:
            base, ext = os.path.splitext(os.path.basename(uploadfiles[k]))
            uploadfiles[k] = config.img_domain+uploadfiles[k][uploadfiles[k].find("static"):].replace(base, base+"_thumb")
        self.render("quote.html", purchaser=purchaser, purchase=purchaseinfo, purchases=purchases, quotes=quotes,
                    reply=(float(reply)/float(len(purchaser_quotes))*100 if len(purchaser_quotes) != 0 else 0),
                    uploadfiles=uploadfiles, quotechances=quotechances)

    @tornado.web.authenticated
    def post(self):
        #验证对X采购单报价
        if self.get_argument("purchaseinfoid") == "":
            self.api_response({'status':'fail','message':'请选择采购单进行报价'})
            return
        #验证表单信息,货源描述,价格,价格说明
        if self.get_argument("quality") == "" or self.get_argument("price") == "":
            self.api_response({'status':'fail','message':'请完整填写'})
            return
        #至少上传一张图片
        uploadfiles = self.session.get("uploadfiles")
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
        quote = self.db.get("select id from quote where userid = %s and purchaseinfoid = %s and state = 0", self.session.get("userid"), self.get_argument("purchaseinfoid"))
        if quote is not None:
            self.api_response({'status':'fail','message':'您已经对次采购单进行过报价,无法再次报价'})
            return
        #不能对自己的采购单进行报价
        mypurchase = self.db.get("select p.id from purchase_info pi,purchase p where p.userid = %s and p.id = pi.purchaseid and pi.id = %s",
                    self.session.get("userid"), self.get_argument("purchaseinfoid"))
        if mypurchase is not None:
            self.api_response({'status':'fail','message':'不能对自己的采购单进行报价'})
            return

        quoteid = self.db.execute_lastrowid("insert into quote(userid,purchaseinfoid,quality,price,`explain`,createtime)value"
                                            "(%s,%s,%s,%s,%s,%s)", self.session.get("userid"),self.get_argument("purchaseinfoid"),
                                            self.get_argument("quality"),self.get_argument("price"),self.get_argument("explain"),
                                            int(time.time()))

        #保存session上传图片的路径
        if uploadfiles:
            for key in uploadfiles:
                self.db.execute("insert into quote_attachment (quoteid, attachment, type)value(%s, %s, %s)", quoteid, uploadfiles[key], key)
            uploadfiles = {}
            self.session["uploadfiles"] = uploadfiles
            self.session.save()

        #给采购商发送通知
        #获得采购商userid
        purchase = self.db.get("select u.nickname,t.* from (select p.userid,pi.name from purchase_info pi,purchase p where pi.purchaseid = p.id and pi.id = %s) "
                               "t,users u where u.id = t.userid",
                               self.get_argument("purchaseinfoid"))
        title = purchase["nickname"].encode('utf-8') + "对您的采购品种【" + purchase["name"].encode('utf-8') + "】进行了报价"

        self.db.execute("insert into notification(sender,receiver,type,title,content,status,createtime)value(%s, %s, %s, %s, %s, %s, %s)",
                        self.session.get("userid"),purchase["userid"],2,title,self.get_argument("purchaseinfoid"),0,int(time.time()))

        self.api_response({'status':'success','message':'请求成功'})

class QuoteUploadHandler(BaseHandler):
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

    @tornado.web.authenticated
    def post(self):
        if self.session.get("uploadfiles"):
            self.session["uploadfiles"] = {}
            self.session.save()
        self.render("quote_success.html")


class WeixinHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("weixin.html")

    @tornado.web.authenticated
    def post(self):
        pass

class QuoteDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, quoteid, nid):
        quote = self.db.get("select * from quote where id = %s", quoteid)
        quote["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(quote["createtime"])))
        quoteattachment = self.db.query("select * from quote_attachment where quoteid = %s", quoteid)
        for qa in quoteattachment:
            base, ext = os.path.splitext(os.path.basename(qa["attachment"]))
            qa["attachment"] = config.img_domain+qa["attachment"][qa["attachment"].find("static"):].replace(base, base+"_thumb")

        #查询采购单信息
        purchaseinfo = self.db.get("select n.*,sp.specification from (select t.*,a.areaname from "
        "(select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.limited,p.term,p.status,p.areaid,p.invoice,pi.id pid,"
        "pi.name,pi.price,pi.quantity,pi.quality,pi.origin,pi.specificationid,pi.views from purchase p,purchase_info pi left join specification s on s.id = pi.specificationid "
        "where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid) n left join "
        "specification sp on n.specificationid = sp.id", quote["purchaseinfoid"])

        #获得采购品种图片
        attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", quote["purchaseinfoid"])
        for attachment in attachments:
            base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
            attachment["attachment"] = config.img_domain+attachment["attachment"][attachment["attachment"].find("static"):].replace(base, base+"_thumb")
        user = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
        purchaseinfo["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(purchaseinfo["createtime"])))
        if purchaseinfo["limited"] == 1:
            purchaseinfo["expire"] = datetime.datetime.utcfromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
            purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
        purchaseinfo["attachments"] = attachments
        print purchaseinfo
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
        print purchaser_quotes
        for purchaser_quote in purchaser_quotes:
            if purchaser_quote.state is not None and purchaser_quote.state != 0:
                reply = reply + 1

        #报价回复消息标记为已读
        result = self.db.execute("update notification set status = 1 where receiver = %s and id = %s", self.session.get("userid"), nid)

        self.render("quote_detail.html", user=user, purchase=purchaseinfo, others=len(others), purchases=purchases,
                    quotes=quotes, acceptuser=acceptuser, reply=int((float(reply)/float(len(purchaser_quotes))*100) if len(purchaser_quotes) != 0 else 0),
                    quote=quote, quoteattachment=quoteattachment)

    @tornado.web.authenticated
    def post(self):
        pass

class QuoteListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        myquotes = self.db.query("select ta.*,n.id nid from (select mq.*,u.nickname,u.type from (select t.*,s.specification from "
                                 "(select ta.*,p.createtime purchasetime,p.term from ("
                                 "select q.*,pi.purchaseid,pi.name,pi.specificationid,pi.origin,pi.quantity,pi.unit "
                                 "from quote q,purchase_info pi where q.purchaseinfoid = pi.id and q.userid = %s order by q.createtime desc"
                                 ") ta,purchase p where ta.purchaseid = p.id) "
                                 "t,specification s where t.specificationid = s.id) mq,users u where mq.userid = u.id) ta "
                                 "left join notification n on ta.userid = n.sender and n.content = ta.purchaseinfoid", userid)
        quoteids = []
        over = 0
        unreply = 0
        for myquote in myquotes:
            quoteids.append(str(myquote.id))
            expire = datetime.datetime.utcfromtimestamp(float(myquote["purchasetime"])) + datetime.timedelta(myquote["term"])
            myquote["timedelta"] = (expire - datetime.datetime.now()).days
            myquote["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(myquote["purchasetime"])))
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
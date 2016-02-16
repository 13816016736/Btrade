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
        purchaseinfo = self.db.get("select tn.*,pa.attachment from (select n.*,sp.specification from (select t.*,a.areaname from "
        "(select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.limited,p.term,p.status,p.areaid,p.invoice,pi.id pid,"
        "pi.name,pi.price,pi.quantity,pi.quality,pi.origin,pi.specificationid,pi.views from purchase p,purchase_info pi left join specification s on s.id = pi.specificationid "
        "where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid) n left join "
        "specification sp on n.specificationid = sp.id) tn left join purchase_attachment pa on tn.pid = pa.purchase_infoid",
                                     purchaseinfoid)

        purchaser = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
        purchaseinfo["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchaseinfo["createtime"])))
        if purchaseinfo["limited"] == 1:
            purchaseinfo["expire"] = datetime.datetime.utcfromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
            purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
        purchaseinfo["attachment"] = "\\static"+purchaseinfo["attachment"] .split("static")[1] if purchaseinfo.get("attachment") else ""

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
            uploadfiles[k] = "\\static"+uploadfiles[k].split("static")[1]
        print uploadfiles
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
        if self.get_argument("quality") == "" or self.get_argument("price") == "" or self.get_argument("explain") == "":
            self.api_response({'status':'fail','message':'请完整填写'})
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

        quoteid = self.db.execute_lastrowid("insert into quote(userid,purchaseinfoid,quality,price,`explain`,createtime)value"
                                            "(%s,%s,%s,%s,%s,%s)", self.session.get("userid"),self.get_argument("purchaseinfoid"),
                                            self.get_argument("quality"),self.get_argument("price"),self.get_argument("explain"),
                                            int(time.time()))

        #保存session上传图片的路径
        uploadfiles = self.session.get("uploadfiles")
        if uploadfiles:
            for key in uploadfiles:
                self.db.execute("insert into quote_attachment (quoteid, attachment, type)value(%s, %s, %s)", quoteid, uploadfiles[key], key)
            uploadfiles = {}
            self.session["uploadfiles"] = uploadfiles
            self.session.save()

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

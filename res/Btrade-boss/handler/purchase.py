# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import json, os, datetime
from utils import *
from config import *
import random
import time
from collections import defaultdict

class PurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, type=-1, starttime=0, endtime=0, page=0):
        page = (int(page) - 1) if page > 0 else 0
        nav = {
            'model': 'purchase/purchaselist/type/'+type+'/starttime/'+starttime+'/endtime/'+endtime,
            'num': self.db.execute_rowcount("select id from purchase"),
        }
        #查询条件
        condition = []
        if int(type) >= 0:
            condition.append("p.status = "+type)
        if starttime !="" and endtime != "":
            condition.append("p.createtime > "+str(int(time.mktime(time.strptime(starttime,'%Y-%m-%d %H:%M')))))
            condition.append("p.createtime < "+str(int(time.mktime(time.strptime(endtime,'%Y-%m-%d %H:%M')))))
        conditionstr = ""
        if condition:
            conditionstr = ("where "+(" and ".join(condition)))
        purchaseinf = defaultdict(list)
        purchases = self.db.query("select t.*,a.areaname from "
                                  "(select p.*,u.nickname,u.name from purchase p left join users u on p.userid = u.id "+
                                  conditionstr + " order by p.createtime desc limit %s,%s) t "
                                  "left join area a on t.areaid = a.id", page * config.conf['POST_NUM'], config.conf['POST_NUM'])

        if purchases:
            purchaseids = [str(purchase["id"]) for purchase in purchases]
            purchaseinfos = self.db.query("select ta.*,count(qu.id) intentions from (select pis.*,q.id qid,count(q.id) quotecount from "
                                          "(select p.*,s.specification from purchase_info p left join specification s on p.specificationid = s.id where p.purchaseid in ("+",".join(purchaseids)+")"
                                          ") pis left join quote q on pis.id = q.purchaseinfoid group by pis.id) ta left join quote qu on ta.qid = qu.id and qu.state = 1 group by ta.id")
            purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
            purchaseattachments = self.db.query("select * from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
            attachments = defaultdict(list)
            for attachment in purchaseattachments:
                attachments[attachment["purchase_infoid"]] = attachment
            for purchaseinfo in purchaseinfos:
                purchaseinfo["attachments"] = attachments.get(purchaseinfo["id"])
                purchaseinf[purchaseinfo["purchaseid"]].append(purchaseinfo)
        for purchase in purchases:
            purchase["purchaseinfo"] = purchaseinf.get(purchase["id"]) if purchaseinf.get(purchase["id"]) else []
            purchase["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchase["createtime"])))
            if purchase["limited"] == 1:
                purchase["expire"] = datetime.datetime.utcfromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
                purchase["timedelta"] = (purchase["expire"] - datetime.datetime.now()).days

        #统计采购单各状态的数量
        results = self.db.query("select status, count(*) count from purchase group by status")
        stat = {}
        for r in results:
            stat[r.status] = r.count
        self.render("purchase.html", purchases=purchases, nav=nav, stat=stat, type=type, starttime=starttime, endtime=endtime)

    def post(self):
        pass

class PurchaseInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, id):
        print id
        purchaseinfo = self.db.get("select n.*,sp.specification from (select t.*,a.areaname from "
        "(select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.limited,p.term,p.status,p.areaid,pi.id pid,"
        "pi.name,pi.price,pi.quantity,pi.origin,pi.quality,pi.specificationid,pi.views from purchase p,purchase_info pi "
        "where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid) n left join "
        "specification sp on n.specificationid = sp.id",id)

        user = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
        #获得采购品种图片
        attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", id)
        for attachment in attachments:
            base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
            attachment["attachment"] = config.img_domain+attachment["attachment"][attachment["attachment"].find("static"):].replace(base, base+"_thumb")
        if purchaseinfo:
            purchaseinfo["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchaseinfo["createtime"])))
            if purchaseinfo["limited"] == 1:
                purchaseinfo["expire"] = datetime.datetime.utcfromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
                purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
            purchaseinfo["attachments"] = attachments
            others = self.db.query("select id from purchase_info where purchaseid = %s and id != %s",
                                          purchaseinfo["id"], purchaseinfo["pid"])
            #获取本采购单报价信息
            quotes = self.db.query("select q.*,u.name,u.nickname,u.phone from quote q left join users u on q.userid = u.id where q.purchaseinfoid = %s", id)
            quoteids = []
            if quotes:
                for quote in quotes:
                    quoteids.append(str(quote.id))
                    quote["datetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(quote["createtime"])))
                quoteattachments = self.db.query("select * from quote_attachment where quoteid in (" + ",".join(quoteids) + ")")
                myquoteattachments = {}
                for quoteattachment in quoteattachments:
                    base, ext = os.path.splitext(os.path.basename(quoteattachment.attachment))
                    quoteattachment.attachment = config.img_domain+quoteattachment.attachment[quoteattachment.attachment.find("static"):].replace(base, base+"_thumb")
                    if myquoteattachments.has_key(quoteattachment.quoteid):
                        myquoteattachments[quoteattachment.quoteid].append(quoteattachment)
                    else:
                        myquoteattachments[quoteattachment.quoteid] = [quoteattachment]
                for mq in quotes:
                    if myquoteattachments.has_key(mq.id):
                        mq["attachments"] = myquoteattachments[mq.id]
                    else:
                        mq["attachments"] = []
            self.render("purchaseinfo.html", user=user, purchase=purchaseinfo, quotes=quotes, others=len(others))
        else:
            self.error("此采购订单不属于你", "/purchase")

    def post(self):
        pass

class RemovePurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        self.db.execute("UPDATE purchase SET status = 0 WHERE id = %s", self.get_argument("pid"))
        self.api_response({'status':'success','message':'请求成功'})

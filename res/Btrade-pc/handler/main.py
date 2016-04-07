# -*- coding: utf-8 -*-

from base import BaseHandler
from collections import defaultdict
# from config import *
import os,config,logging

class MainHandler(BaseHandler):
    def get(self):
        #最新采购单
        purchases = self.db.query("select p.id,p.createtime,u.name,u.type from purchase p left join users u on p.userid = u.id order by p.createtime desc limit 5")
        purchaseids = [str(purchase["id"]) for purchase in purchases]
        purchaseinf = defaultdict(list)
        if purchaseids:
            purchaseinfos = self.db.query("select id,purchaseid,name,specification,origin,quantity,quality,unit from purchase_info where purchaseid in ("+",".join(purchaseids)+")")
            purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
            purchaseattachments = self.db.query("select * from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
            attachments = defaultdict(list)
            for attachment in purchaseattachments:
                attachments[attachment["purchase_infoid"]] = attachment
            purchaseinf = defaultdict(list)
            for purchaseinfo in purchaseinfos:
                purchaseinfo["attachments"] = attachments.get(purchaseinfo["id"])
                purchaseinf[purchaseinfo["purchaseid"]].append(purchaseinfo)
        for purchase in purchases:
            purchase["purchaseinfo"] = purchaseinf.get(purchase["id"])
            purchase["variety"] = len(purchase["purchaseinfo"])

        #最新报价
        quotes = self.db.query("select ta.*,u.name pname from (select t.*,u.name qname from (select qp.*,p.userid puid from "
        "(select q.id,q.userid quid,q.quality,q.price,q.createtime,pi.id pid,pi.purchaseid,pi.name,pi.specification,pi.unit "
        "from quote q,purchase_info pi where q.purchaseinfoid = pi.id order by q.createtime desc limit 4)"
        " qp left join purchase p on qp.purchaseid = p.id) t left join users u on t.quid = u.id) ta left join users u on ta.puid = u.id")
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
        #采购品种总数和报价总数
        pvariety = self.db.execute_rowcount("select id from purchase_info group by varietyid")
        qcount = self.db.execute_rowcount("select id from quote")
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
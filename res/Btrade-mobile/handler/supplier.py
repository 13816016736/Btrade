#coding:utf8
from base import BaseHandler
from utils import *
import config,re
import os,time
from urllib import urlencode

class SupplierDetailHandler(BaseHandler):
    def get(self):
        qid=self.get_argument("qid", "")
        user=None
        transactions=None
        quanlity = self.db.get("select * from quality_supplier where id=%s", qid)
        if quanlity==None:
            self.error(u"没找到该用户","/supplier")
            return
        else:
            user=self.db.get("select id,name,nickname,varietyids,scale,introduce from users where id=%s",quanlity["userid"])
            variety_list = user.varietyids.split(",")
            vl=[]
            for v in variety_list:
                if v!="":
                    vl.append(v)
            supply_variety_name=[]
            if vl!=[]:
                ret = self.db.query("select name from variety where id in (%s) " % ','.join(vl))
                for r in ret:
                    supply_variety_name.append(r.name)
            user.supply_variety_name = supply_variety_name
            quotids=self.db.query("select id from quote where userid=%s",quanlity["userid"])
            if quotids:
                quotids=[str(item["id"]) for item in quotids]
                transactions =self.db.query("select id,purchaseinfoid,quoteid,quantity,unity,price,total,createtime from transaction where status=1 and quoteid in (%s)"%",".join(quotids))
                if transactions:
                    purchaseinfoids = [str(item["purchaseinfoid"]) for item in transactions]
                    purchaseinfos = self.db.query(
                        "select p.userid,pi.id, pi.name,pi.specification from purchase_info pi left join purchase p on pi.purchaseid=p.id where pi.id in(%s)" % ",".join(
                            purchaseinfoids))
                    puserids = [str(item["userid"]) for item in purchaseinfos]
                    purchaseinfomap = dict((i.id, [i.userid, i.name, i.specification]) for i in purchaseinfos)

                    puserinfos = self.db.query(
                        "select id, name,nickname from users where id in (%s)" % ",".join(puserids))
                    pusermap = dict((i.id, [i.name, i.nickname]) for i in puserinfos)



                    for item in transactions:
                        item["varietyname"] = purchaseinfomap[item["purchaseinfoid"]][1]
                        item["specification"] = purchaseinfomap[item["purchaseinfoid"]][2]
                        item["purchasename"] = pusermap[purchaseinfomap[item["purchaseinfoid"]][0]][0]
                        item["purchasenick"] = pusermap[purchaseinfomap[item["purchaseinfoid"]][0]][1]
                        item["createtime"] = time.strftime("%Y-%m-%d", time.localtime(float(item["createtime"])))

                        transactionattachments = self.db.query(
                            "select * from transaction_attachment where transaction_id=%s", item["id"])
                        for attachment in transactionattachments:
                            base, ext = os.path.splitext(os.path.basename(attachment.attachment))
                            attachment.attachment = config.img_domain + attachment.attachment[
                                                                        attachment.attachment.find("static"):].replace(
                                base,
                                base + "_thumb")
                        item["attachments"] = transactionattachments

            varietyimg = self.db.query(
                "select * from quality_attachment where quality_id=%s and type=2", quanlity["id"])
            for qualityattachment in varietyimg:
                base, ext = os.path.splitext(os.path.basename(qualityattachment.attachment))
                qualityattachment.attachment = config.img_domain + qualityattachment.attachment[
                                                                   qualityattachment.attachment.find(
                                                                     "static"):].replace(base, base + "_thumb")
            quanlity["varietyimg"] = varietyimg

            otherimg = self.db.query(
                "select * from quality_attachment where quality_id=%s and type=3", quanlity["id"])

            for qualityattachment in otherimg:
                base, ext = os.path.splitext(os.path.basename(qualityattachment.attachment))
                qualityattachment.attachment = config.img_domain + qualityattachment.attachment[
                                                                   qualityattachment.attachment.find(
                                                                     "static"):].replace(base, base + "_thumb")
            quanlity["otherimg"] = otherimg
        self.render("supplier.html",quanlity=quanlity,user=user,transactions=transactions)
    def post(self):
        pass
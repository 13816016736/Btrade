from base import BaseHandler
from utils import *
import config,re
import os
class SupplierHandler(BaseHandler):
    def get(self):

        self.render("supplier_list.html")
    def post(self):
        pass

class SupplierDetailHandler(BaseHandler):
    def get(self):
        qid=self.get_argument("qid", "")
        user=None
        quanlity = self.db.get("select * from quality_supplier where userid=%s", qid)
        if quanlity:
            self.error("404","/supplier")
        else:
            user=self.db.get("select id,name,nikename,varietyids,scale,introduce where id=%s",quanlity["userid"])
            quotids=self.db.query("select id from quote where userid=%s",quanlity["userid"])
            if quotids:
                quotids=[str(item["id"]) for item in quotids]
                transactions =self.db.query("select id,purchaseinfoid,quoteid,quantity,unity,price,total,createtime from transaction where status=1 and quoteid in (%s)"%",".join(quotids))
                
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
        self.render("supplier.html",quanlity=quanlity,users=user)
    def post(self):
        pass

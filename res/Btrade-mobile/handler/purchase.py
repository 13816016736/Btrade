# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import json, os, datetime, time, base64
from utils import *
from config import *
import random
from collections import defaultdict

class PurchaseHandler(BaseHandler):
    def get(self):
        pass

    def post(self, number=0):
        #列表一项是一个采购单多个品种
        # number = int(number) if number > 0 else 0
        # purchaseinf = defaultdict(list)
        # purchases = self.db.query("select t.*,a.areaname from "
        #                           "(select p.*,u.nickname,u.name from purchase p left join users u on p.userid = u.id order by p.createtime desc limit %s,%s) t "
        #                           "left join area a on t.areaid = a.id", number, config.conf['POST_NUM'])
        # if purchases:
        #     purchaseids = [str(purchase["id"]) for purchase in purchases]
        #     purchaseinfos = self.db.query("select pis.*,count(q.id) quotecount from (select p.*,s.specification from purchase_info p "
        #                                   "left join specification s on p.specificationid = s.id where p.purchaseid in ("+",".join(purchaseids)+")"
        #                                   ") pis left join quote q on pis.id = q.purchaseinfoid group by pis.id")
        #     purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
        #     purchaseattachments = self.db.query("select * from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
        #     attachments = defaultdict(list)
        #     for attachment in purchaseattachments:
        #         attachments[attachment["purchase_infoid"]] = attachment
        #     for purchaseinfo in purchaseinfos:
        #         purchaseinfo["attachments"] = attachments.get(purchaseinfo["id"])
        #         purchaseinf[purchaseinfo["purchaseid"]].append(purchaseinfo)
        #     for purchase in purchases:
        #         purchase["purchaseinfo"] = purchaseinf.get(purchase["id"]) if purchaseinf.get(purchase["id"]) else []
        #         purchase["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchase["createtime"])))
        #         if purchase["limited"] == 1:
        #             # purchase["expire"] = datetime.datetime.utcfromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
        #             expire = datetime.datetime.utcfromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
        #             purchase["timedelta"] = (expire - datetime.datetime.now()).days
        #     print purchaseids
        #     self.api_response({'status':'success', 'list':purchases, 'message':'请求成功'})
        # else:
        #     self.api_response({'status':'nomore','message':'没有更多的采购订单'})
        #列表一项是一个采购单多个品种

        #列表一项是一个采购单一个品种
        number = int(number) if number > 0 else 0
        purchases = self.db.query("select ta.*,u.nickname,u.name from(select pis.*,count(q.id) quotecount from "
                                  "(select t.*,s.specification from (select p.*,pi.id pid,pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specificationid,pi.views from "
                                  "purchase_info pi left join purchase p on p.id = pi.purchaseid order by p.createtime desc limit %s,%s) t "
                                  "left join specification s on t.specificationid = s.id) pis left join quote q on pis.pid = q.purchaseinfoid group by pis.pid) ta "
                                  "left join users u on ta.userid = u.id", number, config.conf['POST_NUM'])
        if purchases:
            purchaseinfoids = [str(purchase["pid"]) for purchase in purchases]
            purchaseattachments = self.db.query("select * from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
            attachments = defaultdict(list)
            for attachment in purchaseattachments:
                attachments[attachment["purchase_infoid"]] = attachment

            for purchase in purchases:
                purchase["purchaseinfo"] = [{"id": purchase["pid"],"name": purchase["name"],"name": purchase["name"],"attachments":attachments.get(purchase["pid"]),
                                             "origin": purchase["origin"],"purchaseid": purchase["id"],"quality": purchase["quality"],
                                             "quantity": purchase["quantity"],"quotecount": purchase["quotecount"],"specification": purchase["specification"],
                                             "specificationid": purchase["specificationid"],"unit": purchase["unit"],"views": purchase["views"]}]
                purchase["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchase["createtime"])))
                if purchase["limited"] == 1:
                    # purchase["expire"] = datetime.datetime.utcfromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
                    expire = datetime.datetime.utcfromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
                    purchase["timedelta"] = (expire - datetime.datetime.now()).days
            print purchases
            print purchaseinfoids
            self.api_response({'status':'success', 'list':purchases, 'message':'请求成功'})
        else:
            self.api_response({'status':'nomore','message':'没有更多的采购订单'})
        #列表一项是一个采购单一个品种

class PurchaseInfoHandler(BaseHandler):
    def get(self, id):
        purchaseinfo = self.db.get("select n.*,sp.specification from (select t.*,a.areaname from "
        "(select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.limited,p.term,p.status,p.areaid,p.invoice,pi.id pid,"
        "pi.name,pi.price,pi.quantity,pi.quality,pi.origin,pi.specificationid,pi.views from purchase p,purchase_info pi left join specification s on s.id = pi.specificationid "
        "where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid) n left join "
        "specification sp on n.specificationid = sp.id",
                                     id)
        #获得采购品种图片
        attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", id)
        for attachment in attachments:
            attachment["attachment"] = "\\static"+attachment["attachment"].split("static")[1] if attachment.get("attachment") else ""
        user = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
        purchaseinfo["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchaseinfo["createtime"])))
        if purchaseinfo["limited"] == 1:
            purchaseinfo["expire"] = datetime.datetime.utcfromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
            purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
        purchaseinfo["attachments"] = attachments

        others = self.db.query("select id from purchase_info where purchaseid = %s and id != %s",
                                      purchaseinfo["id"], purchaseinfo["pid"])

        #此采购商成功采购单数
        purchases = self.db.execute_rowcount("select * from purchase where userid = %s and status = 4", user["id"])
        #此采购单报价数
        quotes = self.db.execute_rowcount("select * from quote where purchaseinfoid = %s", purchaseinfo["pid"])
        #此采购商回复供应商比例
        purchaser_quotes = self.db.query("select p.id,p.userid,t.state state from purchase p left join "
            "(select pi.purchaseid,q.state from purchase_info pi left join quote q on pi.id = q.purchaseinfoid) t "
                "on p.id = t.purchaseid where p.userid = %s", user["id"])
        reply = 0

        for purchaser_quote in purchaser_quotes:
            if purchaser_quote.state is not None and purchaser_quote.state != 0:
                reply = reply + 1

        #浏览数加1
        self.db.execute("update purchase_info set views = views + 1 where id = %s", purchaseinfo["pid"])

        self.render("purchaseinfo.html", user=user, purchase=purchaseinfo, others=len(others), purchases=purchases,
                    quotes=quotes, reply=int((float(reply)/float(len(purchaser_quotes))*100) if len(purchaser_quotes) != 0 else 0))

    def post(self):
        pass

class PurchaseinfoBatchHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, purchaseid):
        purchaseinf = defaultdict(list)
        purchase = self.db.get("select t.*,a.areaname from "
                                  "(select p.*,u.nickname,u.name,u.type from purchase p left join users u on p.userid = u.id where p.id = %s) t"
                                  " left join area a on t.areaid = a.id", purchaseid)
        user = self.db.get("select * from users where id = %s", purchase["userid"])
        if purchase:
            purchaseinfos = self.db.query("select pis.*,count(q.id) quotecount from (select p.*,s.specification from purchase_info p "
                                          "left join specification s on p.specificationid = s.id where p.purchaseid = %s"
                                          ") pis left join quote q on pis.id = q.purchaseinfoid group by pis.id", purchaseid)
            purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
            purchaseattachments = self.db.query("select * from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
            attachments = defaultdict(list)
            for attachment in purchaseattachments:
                attachments[attachment["purchase_infoid"]] = attachment
            for purchaseinfo in purchaseinfos:
                purchaseinfo["attachments"] = attachments.get(purchaseinfo["id"])
                purchaseinf[purchaseinfo["purchaseid"]].append(purchaseinfo)

        purchase["purchaseinfo"] = purchaseinf.get(purchase["id"]) if purchaseinf.get(purchase["id"]) else []
        purchase["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchase["createtime"])))
        if purchase["limited"] == 1:
            purchase["expire"] = datetime.datetime.utcfromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
            purchase["timedelta"] = (purchase["expire"] - datetime.datetime.now()).days
        print purchase

        #此采购商成功采购单数
        purchases = self.db.execute_rowcount("select * from purchase where userid = %s and status = 4", user["id"])
        #此采购商回复供应商比例
        purchaser_quotes = self.db.query("select p.id,p.userid,t.state state from purchase p left join "
            "(select pi.purchaseid,q.state from purchase_info pi left join quote q on pi.id = q.purchaseinfoid) t "
                "on p.id = t.purchaseid where p.userid = %s", user["id"])
        reply = 0
        for purchaser_quote in purchaser_quotes:
            if purchaser_quote.state is not None and purchaser_quote.state != 0:
                reply = reply + 1

        self.render("purchaseinfo_batch.html", user=user, purchase=purchase, purchases=purchases,
                    reply=int((float(reply)/float(len(purchaser_quotes))*100) if len(purchaser_quotes) != 0 else 0))

    @tornado.web.authenticated
    def post(self):
        pass

# class GetCityHandler(BaseHandler):
#
#     def get(self):
#         pass
#
#     def post(self):
#         provinceid = self.get_argument("provinceid")
#         if provinceid == "":
#             self.api_response({'status':'fail','message':'请选择省份'})
#         else:
#             cities = self.db.query("SELECT id,areaname FROM area WHERE parentid = %s", provinceid)
#             self.api_response({'status':'success','message':'请求成功','data':cities})

class UploadFileHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        pass

    @tornado.web.authenticated
    def post(self):
        type = self.get_argument("type")
        base64_string = self.get_argument("base64_string")
        imgData = base64.b64decode(base64_string)
        now = datetime.date.today().strftime("%Y%m%d")
        #文件的暂存路径
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
        upload_path = os.path.join(root_path, 'static\\uploadfiles\\' + now)
        if os.path.exists(upload_path) is False:
            os.mkdir(upload_path)
        name = str(int(time.time())) + str(self.session.get("userid")) + type
        ext = ".png"
        filename = md5(str(name))+ext
        filepath = os.path.join(upload_path,filename)
        with open(filepath,'wb') as up:
            uploadfiles = self.session.get("uploadfiles", {})
            up.write(imgData)
            uploadfiles[type] = filepath
            self.session["uploadfiles"] = uploadfiles
            self.session.save()
            self.api_response({'status':'success','message':'上传成功','path':filepath})
            return

        self.api_response({'status':'fail','message':'上传失败'})

class DeleteFileHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        pass

    @tornado.web.authenticated
    def post(self):
        type = self.get_argument("type")
        uploadfiles = self.session.get("uploadfiles")
        if uploadfiles.has_key(type):
            del uploadfiles[type]
            self.session["uploadfiles"] = uploadfiles
            self.session.save()

        self.api_response({'status':'success','message':'删除成功'})

class GetVarietyInfoHandler(BaseHandler):

    def get(self):
        pass

    def post(self):
        variety = self.get_argument("variety")
        if variety == "":
            self.api_response({'status':'fail','message':'请填写品种'})
        else:
            varietyinfo = self.db.query("SELECT id,name,origin FROM variety WHERE name = %s", variety)
            if len(varietyinfo) == 0:
                self.api_response({'status':'fail','message':'没有该品种'})
            else:
                specifications = self.db.query("SELECT id,specification FROM specification WHERE varietyid = %s", varietyinfo[0]["id"])
                self.api_response({'status':'success','message':'请求成功','list':varietyinfo,'specifications':specifications})

class SaveVarietyHandler(BaseHandler):

    def post(self):
        varietyids = self.get_argument("varietyids")
        if varietyids == "":
            self.api_response({'status':'fail','message':'请填写品种'})
        else:
            print
            result = self.db.execute("update users set varietyids = %s where id = %s", varietyids, self.session.get("userid"))
            if result:
                self.api_response({'status':'fail','message':'没有该品种'})
            else:
                self.api_response({'status':'success','message':'请求成功'})

class RemovePurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        self.db.execute("UPDATE purchase SET status = 0 WHERE id = %s", self.get_argument("pid"))
        self.api_response({'status':'success','message':'请求成功'})

#coding:utf8
import tornado.web
from base import BaseHandler
import os
import config
import time
import datetime
from utils import *
class TransactionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("transaction.html")

    @tornado.web.authenticated
    def post(self):
        pass


class TransactionDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("transaction_info.html")

    @tornado.web.authenticated
    def post(self):
        pass


class TransactionEditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        qid=self.get_argument("qid",None)
        pid=self.get_argument("pid",None)
        tid=self.get_argument("tid",None)
        purchaseinfo=None
        quotesinfo=None
        transaction=None
        if qid and pid:
            purchaseinfo = self.db.get("select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,"
                                       "p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.term,p.status,p.areaid,pi.id pid,"
                                       "pi.name,pi.price,pi.quantity,pi.unit,pi.origin,pi.quality,pi.specification,pi.views,pi.status from purchase p,purchase_info pi "
                                       "where p.id = pi.purchaseid and pi.id = %s", pid)

            ret = self.db.get("select position from area where id =%s", purchaseinfo["areaid"])
            if ret:
                purchaseinfo["position"] = ret.position
            else:
                purchaseinfo["position"] = ""

            user = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
            # 获得采购品种图片
            attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", pid)
            for attachment in attachments:
                base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
                attachment["attachment"] = config.img_domain + attachment["attachment"][
                                                               attachment["attachment"].find("static"):].replace(base,
                                                                                                                 base + "_thumb")
            if purchaseinfo:
                if user:
                    purchaseinfo["uname"]=user["name"]
                    purchaseinfo["unick"]=user["nickname"]
                    purchaseinfo["uphone"]=user["phone"]
                    purchaseinfo["utype"] = user["type"]
                purchaseinfo["datetime"] = time.strftime("%Y-%m-%d %H:%M",
                                                         time.localtime(float(purchaseinfo["createtime"])))
                if purchaseinfo["term"] != 0:
                    purchaseinfo["expire"] = datetime.datetime.fromtimestamp(
                        float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
                    purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
                purchaseinfo["attachments"] = attachments
                # 获取报价信息
                quotesinfo = self.db.get(
                    "select q.*,u.name,u.nickname,u.phone,u.type from quote q left join users u on q.userid = u.id where q.id = %s",
                    qid)
                if quotesinfo:
                    quotesinfo["datetime"] = time.strftime("%Y-%m-%d %H:%M:%S",
                                                          time.localtime(float(quotesinfo["createtime"])))
                    quotesinfo["unit"] = purchaseinfo["unit"]
                    quoteattachments = self.db.query(
                        "select * from quote_attachment where quoteid=%s",qid)
                    for quoteattachment in quoteattachments:
                        base, ext = os.path.splitext(os.path.basename(quoteattachment.attachment))
                        quoteattachment.attachment = config.img_domain + quoteattachment.attachment[
                                                                         quoteattachment.attachment.find(
                                                                             "static"):].replace(base, base + "_thumb")
                    quotesinfo["attachments"] = quoteattachments
            if tid:
                #修改交易记录
                pass
            if not transaction:
                transaction={}
                if purchaseinfo and quotesinfo:
                    if purchaseinfo["unit"]==u"吨":
                        transaction["quantity"]=1000*int(purchaseinfo["quantity"])
                    else:
                        transaction["quantity"] =int(purchaseinfo["quantity"])
                    transaction["price"]=quotesinfo["price"]
                    transaction["total"]=(float(transaction["price"])*transaction["quantity"])/10000


        self.render("transaction_add.html",qid=qid,pid=pid,tid=tid,purchaseinfo=purchaseinfo,quotesinfo=quotesinfo,transaction=transaction)

    @tornado.web.authenticated
    def post(self):
        pass

class TransactionDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        pass

    @tornado.web.authenticated
    def post(self):
        pass

class UploadImageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        pass

    @tornado.web.authenticated
    def post(self):
        now = datetime.date.today().strftime("%Y%m%d")
        root_path = config.img_path
        upload_path = os.path.join(root_path, now)
        if os.path.exists(upload_path) is False:
            os.mkdir(upload_path)
        name = str(int(time.time())) + str(self.session.get("userid"))
        ext = ".png"
        filename = md5(str(name)) + ext
        filepath = os.path.join(upload_path, filename)
        file_metas=self.request.files['img']   #提取表单中‘name’为‘file’的文件元数据
        for meta in file_metas:
            try:
                with open(filepath,'wb') as up:
                    up.write(meta['body'])
                make_thumb(filepath, upload_path, 300, 300)
                self.api_response({'status': 'success', 'message': '上传成功', 'url': filepath})
            except IOError:
                print ' in  IOError'
                self.api_response({'status':'fail','message':'上传失败'})


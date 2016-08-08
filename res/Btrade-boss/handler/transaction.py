#coding:utf8
import tornado.web
from base import BaseHandler
import os
import config
import time
import datetime
from utils import *
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import logging

class TransactionHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        page = self.get_argument("page", 0)
        page = (int(page) - 1) if page > 0 else 0
        transactions = self.db.query("select id,purchaseinfoid,quoteid,quantity,unity,price,total,createtime from transaction where status=1 order by createtime desc limit %s,%s", page * config.conf['POST_NUM'], config.conf['POST_NUM'])
        if transactions:
            purchaseinfoids=[str(item["purchaseinfoid"]) for item in transactions]
            qutoeids=[str(item["quoteid"]) for item in transactions]
            purchaseinfos=self.db.query("select p.userid,pi.id, pi.name,pi.specification from purchase_info pi left join purchase p on pi.purchaseid=p.id where pi.id in(%s)"%",".join(purchaseinfoids))
            puserids=[str(item["userid"]) for item in purchaseinfos]
            purchaseinfomap = dict((i.id, [i.userid,i.name, i.specification]) for i in purchaseinfos)

            puserinfos=self.db.query("select id, name,nickname from users where id in (%s)"%",".join(puserids))
            pusermap= dict((i.id, [i.name, i.nickname]) for i in puserinfos)

            quoteuserinfos=self.db.query("select q.id,u.name,u.nickname from quote q left join users u on q.userid=u.id where q.id in(%s)"%",".join(qutoeids))
            quoteusermap=dict((i.id, [i.name, i.nickname]) for i in quoteuserinfos)

            for item in transactions:
                item["varietyname"]=purchaseinfomap[item["purchaseinfoid"]][1]
                item["specification"]=purchaseinfomap[item["purchaseinfoid"]][2]
                item["purchasename"]=pusermap[purchaseinfomap[item["purchaseinfoid"]][0]][0]
                item["purchasenick"]=pusermap[purchaseinfomap[item["purchaseinfoid"]][0]][1]
                item["quotename"]=quoteusermap[item["quoteid"]][0]
                item["quotenick"]=quoteusermap[item["quoteid"]][1]
                item["createtime"]=time.strftime("%Y-%m-%d %H:%M", time.localtime(float(item["createtime"])))

        nav = {
            'model': 'purchase/transactionlist',
            'cur': page + 1,
            'num': self.db.execute_rowcount("select id from transaction"),
        }

        self.render("transaction.html",transactions=transactions,nav=nav)

    @tornado.web.authenticated
    def post(self):
        pass


class TransactionDetailHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        id=self.get_argument("id",None)
        purchaseinfo = None
        quotesinfo = None
        transaction = None
        tid=id
        pid=None
        qid=None
        if id:
            transaction = self.db.get("select * from transaction where id=%s", id)
            if transaction:
                transactionattachments = self.db.query("select * from transaction_attachment where transaction_id=%s", id)
                for attachment in transactionattachments:
                    base, ext = os.path.splitext(os.path.basename(attachment.attachment))
                    attachment.attachment = config.img_domain + attachment.attachment[
                                                            attachment.attachment.find("static"):].replace(base,
                                                                                                           base + "_thumb")
                transaction["attachments"] = transactionattachments
                pid=transaction.purchaseinfoid
                qid=transaction.quoteid
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


        self.render("transaction_info.html",qid=qid,pid=pid,tid=tid,purchaseinfo=purchaseinfo,quotesinfo=quotesinfo,transaction=transaction)

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
                transaction=self.db.get("select * from transaction where id=%s",tid)
                transactionattachments=self.db.query("select * from transaction_attachment where transaction_id=%s",tid)
                for attachment in transactionattachments:
                    base, ext = os.path.splitext(os.path.basename(attachment.attachment))
                    attachment.attachment = config.img_domain + attachment.attachment[attachment.attachment.find("static"):].replace(base, base + "_thumb")
                transaction["attachments"]=transactionattachments
            if not transaction:
                transaction={}
                if purchaseinfo and quotesinfo:
                    if purchaseinfo["unit"]==u"吨":
                        transaction["quantity"]=1000*int(purchaseinfo["quantity"])
                    else:
                        transaction["quantity"] =int(purchaseinfo["quantity"])
                    transaction["price"]=quotesinfo["price"]
                    transaction["total"]=(float(transaction["price"])*transaction["quantity"])/10000
                    transaction["pay"]=purchaseinfo["pay"]
                    transaction["payinfo"] = purchaseinfo["payinfo"]
                    transaction["payday"] = purchaseinfo["payday"]
                    transaction["delivertime"] =""
                    transaction["checktime"] =""
                    transaction["suppliercomment"] = ""
                    transaction["purchasecomment"] =""
                    transaction["score_to_supplier"] = ""
                    transaction["score_to_purchase"] = ""
                    transaction["attachments"] =[]

        self.render("transaction_add.html",qid=qid,pid=pid,tid=tid,purchaseinfo=purchaseinfo,quotesinfo=quotesinfo,transaction=transaction)

    @tornado.web.authenticated
    def post(self):
        tid=self.get_argument("tid",None)
        pid=self.get_argument("pid",None)
        qid=self.get_argument("qid",None)
        amount=self.get_argument("amount",None)
        price = self.get_argument("price", None)
        sum = self.get_argument("sum", None)
        delivertime=self.get_argument("delivertime", None)
        checktime=self.get_argument("checktime", None)
        paytype=self.get_argument("paytype", None)
        payday=self.get_argument("payday", "")
        if payday!="":
            payday=int(payday)
        else:
            payday=0
        payinfo=self.get_argument("payinfo", "")
        score_to_supplier= self.get_argument("star1", None)
        if score_to_supplier!="":
            score_to_supplier=int(score_to_supplier)
        else:
            score_to_supplier=0
        score_to_purchase = self.get_argument("star2", None)
        if score_to_purchase!="":
            score_to_purchase=int(score_to_purchase)
        else:
            score_to_purchase=0
        suppliercomment=self.get_argument("suppliercomment", None)
        purchasecomment = self.get_argument("purchasecomment", None)

        pics=[1,2,3,4]
        piclist=[]
        for i in pics:
            url=self.get_argument("pic%s"%i, None)
            if url!="":
                rpath = config.img_path
                img_path = rpath[0:rpath.find("static")] + url[url.find("static/"):]#服务器绝对路径
                piclist.append(img_path)
        if tid!="":
            transaction=self.db.get("select * from transaction where id=%s",tid)
            if transaction:
                #修改操作
                self.db.execute("update transaction set quantity=%s,price=%s,total=%s,delivertime=%s,checktime=%s,suppliercomment=%s"
                ",purchasecomment=%s,score_to_supplier=%s,score_to_purchase=%s,pay=%s,payday=%s,payinfo=%s where id=%s"
                                ,amount,price,sum,delivertime,checktime,suppliercomment,purchasecomment,score_to_supplier,score_to_purchase,paytype,payday,payinfo,tid)
                self.db.execute("delete from transaction_attachment where transaction_id=%s",tid)
                for attachment in piclist:
                    self.db.execute("insert into transaction_attachment (attachment,transaction_id) value(%s,%s)",attachment,tid)
                self.api_response(
                    {'status': 'success', 'message': '添加交易记录成功', 'transaction': {'id': tid}, "rtype": "edit"})
        else:
            try:
                lastrowid = self.db.execute_lastrowid(
                "insert into transaction (purchaseinfoid, quoteid, quantity,unity,price,total,delivertime,checktime,suppliercomment,purchasecomment,score_to_supplier,score_to_purchase,pay,payday,payinfo,createtime)"
                    "value(%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    pid, qid, amount, u"元/公斤",price,sum,delivertime,checktime,suppliercomment,purchasecomment,score_to_supplier,score_to_purchase,paytype,payday,payinfo,int(time.time()))
                for attachment in piclist:
                    self.db.execute("insert into transaction_attachment (attachment,transaction_id) value(%s,%s)",attachment,lastrowid)#存图片
                self.api_response({'status': 'success', 'message': '添加交易记录成功', 'transaction': {'id': lastrowid},"rtype":"add"})
            except Exception,ex:
                self.api_response({'status': 'fail', 'message': '添加交易记录失败%s'%str(ex)})


class TransactionDeleteHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        rtype="delete"
        id=self.get_argument("id",None)
        if id:
            self.db.execute("update transaction set status=0 where id=%s",id)
        self.render("transaction_success.html",rtype=rtype)
        pass

    @tornado.web.authenticated
    def post(self):
        pass

class TransactionSuccessHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        rtype=self.get_argument("rtype","add")
        self.render("transaction_success.html",rtype=rtype)

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
        name = str(int(time.time())) + str(self.session.get("userid"))+"boss"
        ext = ".png"
        filename = md5(str(name)) + ext
        filepath = os.path.join(upload_path, filename)
        file_metas=self.request.files['img']   #提取表单中‘name’为‘file’的文件元数据
        for meta in file_metas:
            try:
                with open(filepath,'wb') as up:
                    up.write(meta['body'])
                img_url= config.img_domain + filepath[filepath.find("static"):]
                img = Image.open(filepath)
                width, height = img.size
                self.api_response({'status': 'success', 'message': '上传成功', 'url': img_url,"width":width,"height":height})
            except IOError:
                print ' in  IOError'
                self.api_response({'status':'error','message':'上传失败'})



class CropImageHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        # 获取文件
        imgUrl =self.get_argument("imgUrl")
        #logging.info(imgUrl)
        rpath=config.img_path
        img_path=rpath[0:rpath.find("static")]+imgUrl[imgUrl.find("static/"):]
        #logging.info(img_path)

        #data_stream = cStringIO.StringIO()
        #data_stream.write(imgData)
        source_image = Image.open(img_path)


        # 调成后尺寸
        imgW = self.get_argument("imgW")
        imgH = self.get_argument("imgH")
        imgW, imgH = int(imgW.split(".")[0]), int(imgH.split(".")[0])

        # 偏移量
        imgY1 = self.get_argument("imgY1")
        imgX1 = self.get_argument("imgX1")
        imgY1, imgX1 = int(imgY1), int(imgX1)

        # 裁剪框
        cropW = self.get_argument("cropW")
        cropH = self.get_argument("cropH")
        cropW, cropH = int(cropW), int(cropH)

        # 旋转角度
        angle = self.get_argument("rotation")
        angle = int(angle)

        # 创建新的图片
        source_image = source_image.resize((imgW, imgH))

        rotated_image = source_image.rotate(-float(angle))

        rotated_width, rotated_height = rotated_image.size

        dx = rotated_width - imgW
        dy = rotated_height - imgH

        cropped_rotated_image = Image.new("RGBA", (int(imgW), int(imgH)), 0)
        #a = rotated_image.crop((dx / 2, dy / 2, dx / 2 + imgW, dy / 2 + imgH))
        #a.save("crop.jpeg")
        cropped_rotated_image.paste(rotated_image.crop((dx / 2, dy / 2, dx / 2 + imgW, dy / 2 + imgH)),
                                    (0, 0, imgW, imgH))

        final_image = Image.new("RGBA", (int(cropW), int(cropH)), 0)
        final_image.paste(cropped_rotated_image.crop((imgX1, imgY1, imgX1 + cropW, imgY1 + cropH)),
                          (0, 0, cropW, cropH))

        now = datetime.date.today().strftime("%Y%m%d")
        root_path = config.img_path
        upload_path = os.path.join(root_path, now)
        if os.path.exists(upload_path) is False:
            os.mkdir(upload_path)
        name = str(int(time.time())) + str(self.session.get("userid"))+"boss"
        ext = ".png"
        filename = md5(str(name)) + ext
        filepath = os.path.join(upload_path, filename)
        final_image.save(filepath)
        make_thumb(filepath, upload_path, 300, 300)#生成缩略图
        img_url = config.img_domain + filepath[filepath.find("static"):]
        self.api_response({'status': 'success', 'message': '上传成功', 'url': img_url})
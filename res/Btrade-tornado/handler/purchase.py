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

    def get(self):
        provinces = self.db.query("SELECT id,areaname FROM area WHERE parentid = 0")
        if self.session.get("uploadfiles"):
            self.session["uploadfiles"] = {}
            self.session.save()
        if self.session.get("userid"):
            users = self.db.query("SELECT id,nickname,phone FROM users WHERE id = %s", self.session.get("userid"))
            user_info = self.db.query("SELECT name FROM user_info WHERE userid = %s", self.session.get("userid"))
            if users:
                users[0]["name"] = user_info[0]["name"] if user_info else ""
                self.render("purchase.html", provinces=provinces, users=users[0])
            else:
                self.render("purchase.html", provinces=provinces)
        else:
            self.render("purchase.html", provinces=provinces)

    def post(self):
        data = json.loads(self.request.body)
        if self.current_user is None:#如果未登陆，则先注册
            if data['phone'] is None or data['nickname'] is None or data['verifycode'] is None:
                self.api_response({'status':'fail','message':'采购单位/采购人信息填写不完整'})
            #if data['verifycode'] != self.session.get("verifycode"):
            #   self.api_response({'status':'fail','message':'短信验证码不正确','data':data['phone']})
            username = "ycg_" + datetime.datetime.today().strftime("%Y%m%d%H%M%S")
            password = str(random.randint(100000, 999999))
            lastrowid = self.db.execute_lastrowid("insert into users (username, password, phone, type, nickname, createtime)"
                             "value(%s, %s, %s, %s, %s, %s)", username, md5(str(password + config.salt)), data['phone']
                             , data['type'], data['nickname'], int(time.time()))
            result = self.db.execute("insert into user_info (userid, name)value(%s, %s)", lastrowid, data['name'])
            self.session["userid"] = lastrowid
            self.session["user"] = username
            self.session.save()
            #发短信告知用户登陆名和密码

        data['invoice'] = data['invoice'] if data.has_key('invoice') and data['invoice'] != "" == "" else "0"
        data['pay'] = ",".join(data['pay']) if data.has_key("pay") else ""
        data['payday'] = data['payday'] if data.has_key('payday') and data['payday'] != "" else "0"
        data['send'] = data['send'] if data.has_key('send') and data['send'] != "" else "0"
        data['supplier'] = data['supplier'] if data.has_key('supplier') and data['supplier'] != "" else "0"
        data['limited'] = data['limited'] if data.has_key("limited") else "0"
        data['term'] = data['term'] if data.has_key('term') and data['term'] != "" else "0"
        #存储采购主体信息
        if data.has_key("city"):
            lastrowid = self.db.execute_lastrowid("insert into purchase (userid, areaid, invoice, pay, payday, payinfo,"
                                                  " send, receive, accept, other, supplier, remark, limited, term, createtime)"
                                                  "value(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                                  self.session.get("userid"), data["city"], data['invoice'], data['pay'],
                                                  data['payday'], data['payinfo'], data['send'], data['receive'],
                                                  data['accept'], data['other'], data['supplier'], data['remark'],
                                                  data['limited'], data['term'], int(time.time()))
            #存储采购品种信息
            for i in data['purchases']:
                purchase = data['purchases'][i]
                purchase_infoid = self.db.execute_lastrowid("insert into purchase_info (purchaseid, varietyid, name, specificationid, quantity, unit,"
                                " quality, origin, price)value(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                lastrowid, purchase["varietyid"], purchase['name'], purchase['specification'],
                                purchase['quantity'], purchase['unit'], ",".join(purchase['quality']),
                                ",".join(purchase['origin']), purchase['price'])
                #插入图片
                index = str(int(i) + 1)
                if self.session.get("uploadfiles") and self.session.get("uploadfiles").has_key(index):
                    for attachment in self.session.get("uploadfiles")[index]:
                        self.db.execute("insert into purchase_attachment (purchase_infoid, attachment)"
                                          "value(%s, %s)", purchase_infoid, attachment)
            self.api_response({'status':'success','message':'请求成功'})
        else:
            self.api_response({'status':'fail','message':'必须选择收货地'})

class MyPurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, page=0):
        page = (int(page) - 1) if page > 0 else 0
        nav = {
            'model': 'mypurchase',
            'num': self.db.execute_rowcount("select id from purchase where userid = %s", self.session.get("userid")),
        }
        purchases = self.db.query("select * from purchase where userid = %s limit %s,%s", self.session.get("userid"), page * config.conf['POST_NUM'], config.conf['POST_NUM'])
        purchaseids = [str(purchase["id"]) for purchase in purchases]
        purchaseinf = defaultdict(list)
        if purchaseids:
            purchaseinfos = self.db.query("select p.*,s.specification from purchase_info p left join specification s on p.specificationid = s.id where p.purchaseid in ("+",".join(purchaseids)+")")
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
            purchase["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchase["createtime"])))
            if purchase["limited"] == 1:
                purchase["expire"] = datetime.datetime.utcfromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
                purchase["timedelta"] = (purchase["expire"] - datetime.datetime.now()).days
        self.render("dashboard/mypurchase.html", purchases=purchases, nav=nav)

    def post(self):
        pass

class MyPurchaseInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, id):
        print id
        purchaseinfo = self.db.get("select tn.*,pa.attachment from (select n.*,sp.specification from (select t.*,a.areaname from "
        "(select p.id,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.limited,p.term,p.status,p.areaid,pi.id pid,"
        "pi.name,pi.price,pi.quantity,pi.quality,pi.specificationid from purchase p,purchase_info pi left join specification s on s.id = pi.specificationid "
        "where p.userid = %s and p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid) n left join "
        "specification sp on n.specificationid = sp.id) tn left join purchase_attachment pa on tn.pid = pa.purchase_infoid",
                                     self.session.get("userid"), id)
        if purchaseinfo:
            purchaseinfo["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchaseinfo["createtime"])))
            if purchaseinfo["limited"] == 1:
                purchaseinfo["expire"] = datetime.datetime.utcfromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
                purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
            purchaseinfo["attachment"] = "\\static"+purchaseinfo["attachment"] .split("static")[1] if purchaseinfo.get("attachment") else ""
            print purchaseinfo
            others = self.db.query("select id from purchase_info where purchaseid = %s and id != %s",
                                          purchaseinfo["id"], purchaseinfo["pid"])
            self.render("dashboard/mypurchaseinfo.html", purchase=purchaseinfo, others=len(others))
        else:
            self.error("此采购订单不属于你", "/mypurchase")

    def post(self):
        pass

class GetCityHandler(BaseHandler):

    def get(self):
        pass

    def post(self):
        provinceid = self.get_argument("provinceid")
        if provinceid == "":
            self.api_response({'status':'fail','message':'请选择省份'})
        else:
            cities = self.db.query("SELECT id,areaname FROM area WHERE parentid = %s", provinceid)
            self.api_response({'status':'success','message':'请求成功','data':cities})

class UploadFileHandler(BaseHandler):

    def get(self):
        pass

    def post(self):
        num = self.get_argument("num")
        now = datetime.date.today().strftime("%Y%m%d")
        #文件的暂存路径
        root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
        upload_path = os.path.join(root_path, 'static\\uploadfiles\\' + now)
        if os.path.exists(upload_path) == False:
            os.makedirs(upload_path)
        #提取表单中‘name’为‘file’的文件元数据
        file_metas = self.request.files['filename']
        for meta in file_metas:
            name, ext = os.path.splitext(meta['filename'])
            filename = md5(name.encode('utf-8') + now)+ext
            filepath = os.path.join(upload_path,filename)
            #有些文件需要已二进制的形式存储，实际中可以更改
            with open(filepath,'wb') as up:
                uploadfiles = self.session.get("uploadfiles", {})
                if uploadfiles and uploadfiles.has_key(num):
                    #uploadfiles[num].append(filepath)
                    self.finish(json.dumps({'status':'fail','message':'一个采购单只能传一张图片'}))
                else:
                    up.write(meta['body'])
                    uploadfiles[num] = [filepath]
                    self.session["uploadfiles"] = uploadfiles
                    self.session.save()
                    self.finish(json.dumps({'status':'success','message':'上传成功','path':filepath}))
                print self.session["uploadfiles"]
                return
        self.finish({'status':'fail','message':'上传失败'})

class GetVarietyInfoHandler(BaseHandler):

    def get(self):
        pass

    def post(self):
        variety = self.get_argument("variety")
        if variety == "":
            self.api_response({'status':'fail','message':'请填写品种'})
        else:
            varietyinfo = self.db.get("SELECT id,origin FROM variety WHERE name = %s", variety)
            if len(varietyinfo) == 0:
                self.api_response({'status':'fail','message':'没有该品种'})
            else:
                specifications = self.db.query("SELECT id,specification FROM specification WHERE varietyid = %s", varietyinfo["id"])
                self.api_response({'status':'success','message':'请求成功','varietyinfo':varietyinfo,'specifications':specifications})

class PurchaseSuccessHandler(BaseHandler):

    def get(self):
        self.render("success.html")

    def post(self):
        pass

class RemovePurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        if self.db.query("SELECT count(*) FROM purchase WHERE userid = %s and id = %s", self.session.get("userid"), self.get_argument("pid")):
            self.db.execute("UPDATE purchase SET status = 0 WHERE userid = %s and id = %s", self.session.get("userid"), self.get_argument("pid"))
            self.api_response({'status':'success','message':'请求成功'})
        else:
            self.api_response({'status':'fail','message':'请求失败，此采购订单不属于你'})

class MyPurchaseUpdateHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, id):
        purchases = self.db.query("select * from purchase where userid = %s and id = %s", self.session.get("userid"), id)
        purchaseids = [str(purchase["id"]) for purchase in purchases]
        purchaseinfos = self.db.query("select * from purchase_info where purchaseid in ("+",".join(purchaseids)+")")
        purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
        varietyids = [str(purchaseinfo["varietyid"]) for purchaseinfo in purchaseinfos]
        purchaseattachments = self.db.query("select * from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
        attachments = defaultdict(list)
        for attachment in purchaseattachments:
            attachment["attachment"] = "\\static"+attachment["attachment"] .split("static")[1]
            attachments[attachment["purchase_infoid"]] = attachment
        purchaseinf = defaultdict(list)
        for purchaseinfo in purchaseinfos:
            purchaseinfo["attachments"] = attachments.get(purchaseinfo["id"])
            purchaseinf[purchaseinfo["purchaseid"]].append(purchaseinfo)
        for purchase in purchases:
            purchase["purchaseinfo"] = purchaseinf[purchase["id"]]

        if self.session.get("uploadfiles"):
            self.session["uploadfiles"] = {}
            self.session.save()
        provinces = self.db.query("SELECT id,areaname FROM area WHERE parentid = 0")
        area = self.db.get("SELECT id,parentid FROM area WHERE id = %s", purchase["areaid"])
        city = self.db.query("SELECT id,areaname FROM area WHERE parentid = %s", area.get("parentid"))
        user = self.db.get("SELECT id,nickname,phone FROM users WHERE id = %s", self.session.get("userid"))
        # user_info = self.db.get("SELECT name FROM user_info WHERE userid = %s", self.session.get("userid"))
        specifications = self.db.query("select * from specification where varietyid in ("+",".join(varietyids)+")")
        specificationinf = defaultdict(list)
        for specification in specifications:
            specificationinf[specification["varietyid"]].append(specification)
        for purchaseinfo in purchase["purchaseinfo"]:
            for index,spec in specificationinf.items():
                if index == purchaseinfo["varietyid"]:
                    purchaseinfo["specification"] = spec
                    break
        print user
        if user:
            self.render("updatepurchase.html", purchase=purchase, provinces=provinces, city=city, area=area, user=user)
        else:
            self.error("此用户不存在", "/login")

    @tornado.web.authenticated
    def post(self, id):
        purchaseinfo = self.db.query("select * from purchase where id = %s and userid = %s", id, self.session.get("userid"))
        if len(purchaseinfo) == 0:
            self.api_response({'status':'fail','message':'此采购订单不属于你'})
            return
        data = json.loads(self.request.body)
        data['invoice'] = data['invoice'] if data.has_key('invoice') and data['invoice'] != "" == "" else "0"
        data['pay'] = ",".join(data['pay']) if data.has_key("pay") else ""
        data['payday'] = data['payday'] if data.has_key('payday') and data['payday'] != "" else "0"
        data['send'] = data['send'] if data.has_key('send') and data['send'] != "" else "0"
        data['supplier'] = data['supplier'] if data.has_key('supplier') and data['supplier'] != "" else "0"
        data['limited'] = data['limited'] if data.has_key("limited") else "0"
        data['term'] = data['term'] if data.has_key('term') and data['term'] != "" else "0"
        print data
        #存储采购主体信息
        if data.has_key("city"):
            self.db.execute("update purchase set areaid=%s, invoice=%s, pay=%s, payday=%s, payinfo=%s,"
                                                  " send=%s, receive=%s, accept=%s, other=%s, supplier=%s, remark=%s,"
                                                  " limited=%s, term=%s, createtime=%s where id = %s and userid = %s",
                                                  data["city"], data['invoice'], data['pay'], data['payday'],
                                                  data['payinfo'], data['send'], data['receive'], data['accept'],
                                                  data['other'], data['supplier'], data['remark'], data['limited'],
                                                  data['term'], int(time.time()), id, self.session.get("userid"))
            #搜出当前采购单中的品种，以备下面插入新采购单后删除
            purchaseinfos = self.db.query("select id from purchase_info where purchaseid = %s", id)
            purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
            print purchaseinfoids
            #存储采购品种信息
            for i in data['purchases']:
                purchase = data['purchases'][i]
                purchase_infoid = self.db.execute_lastrowid("insert into purchase_info (purchaseid, varietyid, name, specificationid, quantity, unit,"
                                " quality, origin, price)value(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                id, purchase["varietyid"], purchase['name'], purchase['specification'],
                                purchase['quantity'], purchase['unit'], ",".join(purchase['quality']),
                                ",".join(purchase['origin']), purchase['price'])
                #插入图片
                index = str(int(i) + 1)
                if self.session.get("uploadfiles") and self.session.get("uploadfiles").has_key(index):
                    for attachment in self.session.get("uploadfiles")[index]:
                        self.db.execute("insert into purchase_attachment (purchase_infoid, attachment)"
                                          "value(%s, %s)", purchase_infoid, attachment)

            #删除采购品种带的附件
            self.db.execute("delete from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
            #删除采购品种
            self.db.execute("delete from purchase_info where id in ("+",".join(purchaseinfoids)+")")
            self.api_response({'status':'success','message':'请求成功'})
        else:
            self.api_response({'status':'fail','message':'必须选择收货地'})
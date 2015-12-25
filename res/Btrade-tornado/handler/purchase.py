# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import json, os, datetime
from utils import *
from config import *
import random
import time

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

        print data
        data['invoice'] = data['invoice'] if data.has_key('invoice') and data['invoice'] != "" == "" else "0"
        data['pay'] = ",".join(data['pay']) if data.has_key("pay") else ""
        data['payday'] = data['payday'] if data.has_key('payday') and data['payday'] != "" else "0"
        data['send'] = data['send'] if data.has_key('send') and data['send'] != "" else "0"
        data['supplier'] = data['supplier'] if data.has_key('supplier') and data['supplier'] != "" else "0"
        data['limited'] = ",".join(data['limited']) if data.has_key("limited") else ""
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
                        self.db.execute_lastrowid("insert into purchase_attachment (purchase_infoid, attachment)"
                                          "value(%s, %s)", purchase_infoid, attachment)
            self.api_response({'status':'success','message':'请求成功'})
        else:
            self.api_response({'status':'faile','message':'必须选择收货地'})

class MyPurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("dashboard/mypurchase.html")

    def post(self):
        pass

class MyPurchaseInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, id):
        print id
        self.render("dashboard/mypurchaseinfo.html")

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
                up.write(meta['body'])
                self.finish(json.dumps({'status':'success','message':'上传成功','path':filepath}))
                uploadfiles = self.session.get("uploadfiles")
                if uploadfiles and uploadfiles.has_key(num):
                    uploadfiles[num].append(filepath)
                else:
                    uploadfiles = {}
                    uploadfiles[num] = [filepath]
                self.session["uploadfiles"] = uploadfiles
                self.session.save()
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
            varietyinfo = self.db.query("SELECT id,origin FROM variety WHERE name = %s", variety)
            if len(varietyinfo) == 0:
                self.api_response({'status':'fail','message':'没有该品种'})
            else:
                specifications = self.db.query("SELECT id,specification FROM specification WHERE varietyid = %s", varietyinfo[0]["id"])
                self.api_response({'status':'success','message':'请求成功','varietyinfo':varietyinfo[0],'specifications':specifications})

class PurchaseSuccessHandler(BaseHandler):

    def get(self):
        self.render("success.html")

    def post(self):
        pass
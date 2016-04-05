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
            for key, uploadfiles in self.session.get("uploadfiles").items():
                for uploadfile in  uploadfiles:
                    # uploadfile = uploadfile.encode("utf-8")
                    if os.path.isfile(uploadfile):
                        os.remove(uploadfile)
                        base, ext = os.path.splitext(os.path.basename(uploadfile))
                        filename = uploadfile.replace(base, base+"_thumb")
                        os.remove(filename)
            self.session["uploadfiles"] = {}
            self.session.save()
        if self.session.get("userid"):
            user = self.db.get("SELECT id,username,name,nickname,phone,type,varietyids FROM users WHERE id = %s", self.session.get("userid"))
            if user:
                #最近采购品种，id,name,origin
                mypurchase = self.db.query("select v.id,v.name,v.origin from "
                                           "(select pi.varietyid from purchase p left join purchase_info pi on p.id = pi.purchaseid where p.userid = %s) t "
                                           "left join variety v on t.varietyid = v.id group by v.id", self.session.get("userid"))
                #我关注的品种，id,name,origin
                varietys = []
                if user["varietyids"]:
                    varietys = self.db.query("SELECT id,name,origin FROM variety WHERE id in ("+user["varietyids"]+")")
                user["name"] = user.get("name")
                self.render("purchase.html", provinces=provinces, user=user, mypurchase=mypurchase, varietys=varietys)
            else:
                self.render("purchase.html", provinces=provinces)
        else:
            self.render("purchase.html", provinces=provinces)

    def post(self):
        data = {}
        for key,arg in self.request.arguments.iteritems():
            if key == 'purchases':
                data[key] = eval(arg[0])
            else:
                data[key] = arg[0]
        if self.current_user is None or self.current_user == "":#如果未登陆，则先注册
            if data['phone'] is None or data['name'] is None or data['smscode'] is None:
                self.api_response({'status':'fail','message':'采购单位/采购人信息填写不完整'})
                return
            if data['smscode'] != self.session.get("smscode"):
                self.api_response({'status':'fail','message':'短信验证码不正确','data':data['phone']})
                return
            username = "ycg" + time.strftime("%y%m%d%H%M%S")
            password = str(random.randint(100000, 999999))
            lastrowid = self.db.execute_lastrowid("insert into users (username, password, phone, type, name, nickname, createtime)"
                             "value(%s, %s, %s, %s, %s, %s, %s)", username, md5(str(password + config.salt)), data['phone']
                             , data['type'], data['name'], data['username'], int(time.time()))
            self.session["userid"] = lastrowid
            self.session["user"] = username
            self.session.save()
            #发短信告知用户登陆名和密码
            regInfo(data['phone'], username, password)

        data['invoice'] = data['invoice'] if data.has_key('invoice') and data['invoice'] != "" else "0"
        data['paytype'] = data['paytype'] if data.has_key("paytype") and data['paytype'] != "" else "0"
        data['payday'] = data['payday'] if data.has_key('payday') and data['payday'] != "" else "0"
        data['payinfo'] = data['payinfo'] if data.has_key('payinfo') and data['payinfo'] != "" else ""
        data['sample'] = data['sample'] if data.has_key('sample') and data['sample'] != "" else "0"
        data['permit'] = data['permit'] if data.has_key('permit') and data['permit'] != "" else "0"
        data['deadline'] = data['deadline'] if data.has_key('deadline') and data['deadline'] != "" else "0"
        #存储采购主体信息
        if data.has_key("address"):
            # purchaseid = get_purchaseid()
            # self.db.execute("insert into purchase (id, userid, areaid, invoice, pay, payday, payinfo,"
            #                                       " send, receive, accept, other, supplier, remark, limited, term, createtime)"
            #                                       "value(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            #                                       purchaseid, self.session.get("userid"), data["address"], data['invoice'], data['paytype'],
            #                                       data['payday'], data['payinfo'], data['sample'], data['contact'],
            #                                       data['demand'], data['replenish'], data['permit'], data['others'],0,
            #                                       data['deadline'], int(time.time()))
            # #存储采购品种信息
            # varids = []
            # for i,purchase in data['purchases'].iteritems():
            #     varids.append(purchase["nVarietyId"])
            #     purchase['nPrice'] = purchase['nPrice'] if purchase['nPrice'] else 0
            #     purchase_infoid = self.db.execute_lastrowid("insert into purchase_info (purchaseid, varietyid, name, specification, quantity, unit,"
            #                     " quality, origin, price)value(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            #                     purchaseid, purchase["nVarietyId"], purchase['nVariety'], purchase['nRank'],
            #                     purchase['nQuantity'], purchase['nUnit'], ",".join([ q for q in purchase['nQuality'] if q != '' ]),
            #                     ",".join([ a for a in purchase['nArea'] if a != '' ]), purchase['nPrice'])
            #     #插入图片
            #     if self.session.get("uploadfiles") and self.session.get("uploadfiles").has_key(i):
            #         for attachment in self.session.get("uploadfiles")[i]:
            #             self.db.execute("insert into purchase_attachment (purchase_infoid, attachment)"
            #                               "value(%s, %s)", purchase_infoid, attachment)
            #         self.session["uploadfiles"] = {}
            #         self.session.save()
            status,purchaseid,varids = purchasetransaction(self, data)
            if status:
                self.api_response({'status':'success','message':'请求成功','data':varids,'purchaseid':purchaseid})
            else:
                self.api_response({'status':'fail','message':'发布失败，请刷新页面重试'})
        else:
            self.api_response({'status':'fail','message':'必须选择收货地'})

class MyPurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, type=-1, starttime=0, endtime=0, page=0):
        page = (int(page) - 1) if page > 0 else 0
        nav = {
            'model': 'mypurchase/type/'+type+'/starttime/'+starttime+'/endtime/'+endtime,
            'num': self.db.execute_rowcount("select id from purchase where userid = %s", self.session.get("userid")),
        }
        #查询条件
        condition = []
        if int(type) >= 0:
            condition.append("p.status = "+type)
        if starttime !="" and endtime != "":
            condition.append("p.createtime > "+str(int(time.mktime(time.strptime(starttime,'%Y-%m-%d')))))
            condition.append("p.createtime < "+str(int(time.mktime(time.strptime(endtime,'%Y-%m-%d')))))
        conditionstr = ""
        if condition:
            conditionstr = ("and "+(" and ".join(condition)))
        purchases = self.db.query("select p.*,u.nickname,u.name from purchase p left join users u on p.userid = u.id where p.userid = %s "+conditionstr+" order by p.createtime desc limit %s,%s", self.session.get("userid"), page * config.conf['POST_NUM'], config.conf['POST_NUM'])
        purchaseids = [str(purchase["id"]) for purchase in purchases]
        purchaseinf = defaultdict(list)
        if purchaseids:
            purchaseinfos = self.db.query("select ta.*,count(qu.id) intentions from (select p.*,q.id qid,count(q.id) quotecount,min(CAST(q.price as SIGNED)) qprice"
                " from purchase_info p left join quote q on p.id = q.purchaseinfoid where p.purchaseid in ("+",".join(purchaseids)+") group by p.id"
                ") ta left join quote qu on ta.qid = qu.id and qu.state = 1 group by ta.id")
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
            if purchase["term"] != 0:
                purchase["expire"] = datetime.datetime.fromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
                purchase["timedelta"] = (purchase["expire"] - datetime.datetime.now()).days

        #统计采购单各状态的数量
        results = self.db.query("select status, count(*) count from purchase where userid = %s group by status", self.session.get("userid"))
        stat = {}
        for r in results:
            stat[r.status] = r.count

        self.render("dashboard/mypurchase.html", purchases=purchases, nav=nav, stat=stat, type=type, starttime=starttime, endtime=endtime)

    def post(self):
        pass

class MyPurchaseInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, id):
        print id
        purchaseinfo = self.db.get("select t.*,a.areaname from (select p.id,p.invoice,p.pay,p.payday,p.payinfo,p.accept,p.send,"
        "p.receive,p.other,p.supplier,p.remark,p.createtime,p.term,p.status,p.areaid,pi.id pid,"
        "pi.name,pi.price,pi.quantity,pi.origin,pi.quality,pi.specification,pi.views from purchase p,purchase_info pi "
        "where p.userid = %s and p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid",self.session.get("userid"), id)
        #获得采购品种图片
        attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", id)
        for attachment in attachments:
            base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
            attachment["attachment"] = config.img_domain+attachment["attachment"][attachment["attachment"].find("static"):].replace(base, base+"_thumb")
        if purchaseinfo:
            purchaseinfo["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchaseinfo["createtime"])))
            if purchaseinfo["term"] != 0:
                purchaseinfo["expire"] = datetime.datetime.fromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
                purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
            purchaseinfo["attachments"] = attachments
            others = self.db.query("select id from purchase_info where purchaseid = %s and id != %s",
                                          purchaseinfo["id"], purchaseinfo["pid"])

            #获取本采购单报价信息
            quotes = self.db.query("select q.*,u.name,u.nickname,u.phone,u.type from quote q left join users u on q.userid = u.id where q.purchaseinfoid = %s", id)
            quoteids = []
            mprice = None
            if quotes:
                mprice = quotes[0]["price"]
                for quote in quotes:
                    if mprice > int(quote.price):
                        mprice = quote.price
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
            self.render("dashboard/mypurchaseinfo.html", purchase=purchaseinfo, quotes=quotes, mprice=mprice, others=len(others))
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
        root_path = config.img_path
        upload_path = os.path.join(root_path, now)
        if os.path.exists(upload_path) is False:
            os.makedirs(upload_path)
        #提取表单中‘name’为‘file’的文件元数据
        file_metas = self.request.files['filename']
        for meta in file_metas:
            base = md5(str(time.time()))
            filename = base + ".png"
            filepath = os.path.join(upload_path,filename)
            #有些文件需要已二进制的形式存储，实际中可以更改
            uploadfiles = self.session.get("uploadfiles", {})
            if uploadfiles and uploadfiles.has_key(num):
                #uploadfiles[num].append(filepath)
                self.finish(json.dumps({'status':'fail','message':'一个采购单只能传一张图片'}))
                return
            else:
                with open(filepath,'wb') as up:
                    up.write(meta['body'])
                #生成缩略图
                make_thumb(filepath,upload_path,300,300)
                uploadfiles[num] = [filepath]
                self.session["uploadfiles"] = uploadfiles
                self.session.save()
                thumbfile = config.img_domain+filepath[filepath.find("static"):].replace(base, base+"_thumb")
                self.finish(json.dumps({'status':'success','message':'上传成功','path':thumbfile}))
                print self.session["uploadfiles"]
                return
        self.finish({'status':'fail','message':'上传失败'})

class DeleteFileHandler(BaseHandler):

    def get(self):
        pass

    def post(self):
        num = self.get_argument("num")
        uploadfiles = self.session.get("uploadfiles")
        if uploadfiles.has_key(num):
            for file in uploadfiles[num]:
                if os.path.isfile(file):
                    os.remove(file)
                    base, ext = os.path.splitext(os.path.basename(file))
                    filename = file.replace(base, base+"_thumb")
                    os.remove(filename)
                    del uploadfiles[num]
                    self.session["uploadfiles"] = uploadfiles
                    self.session.save()
                    self.api_response({'status':'success','message':'删除成功'})
                else:
                    del uploadfiles[num]
                    self.session["uploadfiles"] = uploadfiles
                    self.session.save()
                    self.api_response({'status':'fail','message':'文件不存在'})
        else:
            self.api_response({'status':'success','message':'文件路径不存在'})

class GetVarietyInfoHandler(BaseHandler):

    def get(self):
        pass

    def post(self):
        variety = self.get_argument("variety")
        if variety == "":
            self.api_response({'status':'fail','message':'请填写品种'})
        else:
            varietyinfo = self.db.query("SELECT id,name,origin FROM variety WHERE name like %s", variety+"%")
            if len(varietyinfo) == 0:
                self.api_response({'status':'fail','message':'没有该品种'})
            else:
                self.api_response({'status':'success','message':'请求成功','list':varietyinfo})


class GetVarInfoByIdHandler(BaseHandler):

    def post(self):
        varietyid = self.get_argument("varietyid")
        if varietyid == "":
            self.api_response({'status':'fail','message':'请填写品种'})
        else:
            varietyinfo = self.db.get("SELECT id,specification,origin FROM variety WHERE id = %s", varietyid)
            if len(varietyinfo) == 0:
                self.api_response({'status':'fail','message':'没有该品种'})
            else:
                specifications = varietyinfo['specification'].split(",")
                spec = []
                for s in specifications:
                    val = {}
                    val["val"] = 0
                    val["text"] = s
                    spec.append(val)
                self.api_response({'status':'success','message':'请求成功','rank':spec,'unit':[{'val':'1','text':'公斤'}],'txt':'公斤'})

class PurchaseSuccessHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        varids = self.get_argument("varids")
        variety = self.db.query("select name from variety where id in ("+varids+")")
        varname = []
        for v in variety:
            varname.append("["+v["name"]+"]")
        suppliers = self.db.query("select ta.name,a.areaname,a.parentid from "
                                  "(select u.name,u.areaid from "
                                  "(SELECT pi.id,n.sender FROM `purchase_info` pi,notification n WHERE pi.id = n.content and n.type = 2 and varietyid in ("
                                  +varids+") and n.sender != %s) t left join users u on t.sender = u.id) ta left join area a on ta.areaid = a.id ", self.session.get("userid"))

        self.render("success.html", varname=",".join(varname), suppliers=suppliers, purchaseid=self.get_argument("purchaseid"))

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
        purchases = self.db.query("select * from purchase where userid = %s", self.session.get("userid"))
        bool = True
        for p in purchases:
            if p["id"] == id:
                bool = False
                purchase = p
        if bool:
            self.error("此采购单不属于你", "/mypurchase")
            return

        purchaseids = [str(p["id"]) for p in purchases]
        user = self.db.get("SELECT id,username,name,nickname,phone,type,varietyids FROM users WHERE id = %s", self.session.get("userid"))
        #最近采购品种，id,name,origin
        mypurchasevar = self.db.query("select v.id,v.name,v.origin from purchase_info pi left join variety v on pi.varietyid = v.id where pi.purchaseid in ("+",".join(purchaseids)+") group by v.id")
        #我关注的品种，id,name,origin
        varietys = []
        if user["varietyids"]:
            varietys = self.db.query("SELECT id,name,origin FROM variety WHERE id in ("+user["varietyids"]+")")

        purchaseinfos = self.db.query("select pi.*,v.id varietyid,v.specification allspec,v.origin allorigin from purchase_info pi left join variety v on pi.varietyid = v.id where pi.purchaseid = %s",id)
        purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
        varietyids = [str(purchaseinfo["varietyid"]) for purchaseinfo in purchaseinfos]
        purchaseattachments = self.db.query("select * from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
        attachments = defaultdict(list)
        for attachment in purchaseattachments:
            attachment["path"] = attachment["attachment"]
            base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
            attachment["attachment"] = config.img_domain+attachment["attachment"][attachment["attachment"].find("static"):].replace(base, base+"_thumb")
            attachments[attachment["purchase_infoid"]] = attachment
        purchaseinf = defaultdict(list)
        uploadfiles = self.session.get("uploadfiles", {})
        for index, purchaseinfo in enumerate(purchaseinfos):
            i = str(index+1)
            purchaseinfo["attachments"] = attachments.get(purchaseinfo["id"])
            # if purchaseinfo["attachments"] and uploadfiles and uploadfiles.has_key(i):
            #     #uploadfiles[num].append(filepath)
            #     base, ext = os.path.splitext(os.path.basename(uploadfiles[i][0]))
            #     purchaseinfo["attachments"]['attachment'] = config.img_domain+uploadfiles[i][0][uploadfiles[i][0].find("static"):].replace(base, base+"_thumb")
            # elif purchaseinfo["attachments"]:
            #     uploadfiles[i] = [purchaseinfo["attachments"]["path"]]
            if purchaseinfo["attachments"]:
                uploadfiles[i] = [purchaseinfo["attachments"]["path"]]
            purchaseinf[purchaseinfo["purchaseid"]].append(purchaseinfo)

        self.session["uploadfiles"] = uploadfiles
        self.session.save()
        print self.session["uploadfiles"]
        provinces = self.db.query("SELECT id,areaname FROM area WHERE parentid = 0")
        area = self.db.get("SELECT id,parentid,areaname FROM area WHERE id = %s", purchase["areaid"])
        city = self.db.query("SELECT id,areaname FROM area WHERE parentid = %s", area.get("parentid"))

        # specifications = self.db.query("select * from specification where varietyid in ("+",".join(varietyids)+")")
        # specificationinf = defaultdict(list)
        # for specification in specifications:
        #     specificationinf[specification["varietyid"]].append(specification)
        purchase["purchaseinfo"] = purchaseinf[id]
        for purchaseinfo in purchase["purchaseinfo"]:
            purchaseinfo["allspec"] = purchaseinfo["allspec"].split(",")
        purchase["supplier"] = purchase["supplier"].split("&")
        print purchase
        if user:
            self.render("updatepurchase.html", purchase=purchase, provinces=provinces, city=city, area=area, user=user, mypurchasevar=mypurchasevar, varietys=varietys)
        else:
            self.error("此用户不存在", "/login")

    @tornado.web.authenticated
    def post(self, id):
        purchaseinfo = self.db.query("select * from purchase where id = %s and userid = %s", id, self.session.get("userid"))
        if len(purchaseinfo) == 0:
            self.api_response({'status':'fail','message':'此采购订单不属于你'})
            return
        data = {}
        for key,arg in self.request.arguments.iteritems():
            if key == 'purchases':
                data[key] = eval(arg[0])
            else:
                data[key] = arg[0]
        data['invoice'] = data['invoice'] if data.has_key('invoice') and data['invoice'] != "" else "0"
        data['paytype'] = data['paytype'] if data.has_key("paytype") and data['paytype'] != "" else "0"
        data['payday'] = data['payday'] if data.has_key('payday') and data['payday'] != "" else "0"
        data['payinfo'] = data['payinfo'] if data.has_key('payinfo') and data['payinfo'] != "" else ""
        data['sample'] = data['sample'] if data.has_key('sample') and data['sample'] != "" else "0"
        data['permit'] = data['permit'] if data.has_key('permit') and data['permit'] != "" else "0"
        data['deadline'] = data['deadline'] if data.has_key('deadline') and data['deadline'] != "" else "0"
        #contact demand replenish others
        #存储采购主体信息
        if data.has_key("address"):
            # self.db.execute("update purchase set areaid=%s, invoice=%s, pay=%s, payday=%s, payinfo=%s,"
            #                                       " send=%s, receive=%s, accept=%s, other=%s, supplier=%s, remark=%s,"
            #                                       " limited=%s, term=%s, createtime=%s where id = %s and userid = %s",
            #                                       data["address"], data['invoice'], data['paytype'], data['payday'],
            #                                       data['payinfo'], data['sample'], data['contact'], data['demand'],
            #                                       data['replenish'], data['permit'], data['others'], 0,
            #                                       data['deadline'], int(time.time()), id, self.session.get("userid"))
            # #搜出当前采购单中的品种，以备下面插入新采购单后删除
            # purchaseinfos = self.db.query("select id from purchase_info where purchaseid = %s", id)
            # purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
            # #存储采购品种信息
            # varids = []
            # for i,purchase in data['purchases'].iteritems():
            #     varids.append(purchase["nVarietyId"])
            #     purchase['nPrice'] = purchase['nPrice'] if purchase['nPrice'] else 0
            #     purchase_infoid = self.db.execute_lastrowid("insert into purchase_info (purchaseid, varietyid, name, specification, quantity, unit,"
            #                     " quality, origin, price)value(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            #                     id, purchase["nVarietyId"], purchase['nVariety'], purchase['nRank'],
            #                     purchase['nQuantity'], purchase['nUnit'], ",".join([ q for q in purchase['nQuality'] if q != '' ]),
            #                     ",".join([ a for a in purchase['nArea'] if a != '' ]), purchase['nPrice'])
            #     #插入图片
            #     if self.session.get("uploadfiles") and self.session.get("uploadfiles").has_key(i):
            #         for attachment in self.session.get("uploadfiles")[i]:
            #             self.db.execute("insert into purchase_attachment (purchase_infoid, attachment)"
            #                               "value(%s, %s)", purchase_infoid, attachment)
            # self.session["uploadfiles"] = {}
            # self.session.save()
            # #删除采购品种带的附件
            # attach = self.db.query("select attachment from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
            # for a in attach:
            #     os.remove(a["attachment"])
            # self.db.execute("delete from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
            # #删除采购品种
            # self.db.execute("delete from purchase_info where id in ("+",".join(purchaseinfoids)+")")
            status,varids = updatepurchase(self, id, data)
            if status:
                self.api_response({'status':'success','message':'请求成功','data':varids})
            else:
                self.api_response({'status':'fail','message':'修改失败请刷新页面重试'})
        else:
            self.api_response({'status':'fail','message':'必须选择收货地'})

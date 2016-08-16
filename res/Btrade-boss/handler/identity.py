#coding:utf8
import tornado.web
from base import BaseHandler
import os
import config
import time
import datetime
from utils import *
from datetime import timedelta,datetime

class IdentifyUserHandler(BaseHandler):
    def get(self):
        pass
    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        qid = self.get_argument("qid", None)
        usertype=self.get_argument("usertype",None)
        address = self.get_argument("address", None)
        if int(usertype)!=1:
            compny=self.get_argument("compny",None)
            if compny==""or address=="":
                self.api_response(
                    {'status': 'error', 'message': '公司名称和地址不能为空'})
                return
        else:
            compny =""
            if address=="":
                self.api_response(
                    {'status': 'error', 'message': '地址不能为空'})
                return
        name = self.get_argument("realname", None)
        identifiers = self.get_argument("idnumber", None)
        if int(usertype)==1:
            pics = [1, 2, 3]
        else:
            pics = [1, 2, 3, 4,5,6,7]
        piclist = []
        for i in pics:
            describe=""
            if int(usertype)==1:
                if i==1:
                    describe="本人头像"
                elif i==2:
                    describe ="身份证正面"
                elif i==3:
                    describe = "种植基地照片"
            else:
                if i==1:
                    describe="企业全景"
                elif i==2:
                    describe ="联系人身份证正面"
                elif i==3:
                    describe = "法人身份证正面"
                elif i==4:
                    describe = "营业执照"
                elif i == 5:
                    describe = "GSP证书"
                elif i == 6:
                    describe = "中草药收购证"
                elif i == 7:
                    describe = "授权书2.0"
            url = self.get_argument("pic%s" % i, None)
            if url != "":
                rpath = config.img_path
                img_path = rpath[0:rpath.find("static")] + url[url.find("static/"):]  # 服务器绝对路径
                item={"path":img_path,"describe":describe}
                piclist.append(item)
        if qid!="":
            transaction=self.db.get("select * from quality_supplier where id=%s",qid)
            if transaction:
                #修改操作
                self.db.execute("update quality_supplier set type=%s,name=%s,identifiers=%s,company=%s,address=%s where id=%s"
                                ,usertype,name,identifiers,compny,address,qid)
                attachments=self.db.query("select * from quality_attachment where quality_id=%s and type=1",qid)
                plist=[item["path"]for item in piclist]
                for item in attachments:#删除不要的图片文件
                    if item["attachment"] in plist:
                        continue
                    try:
                        rpath = config.img_path
                        base, ext = os.path.splitext(os.path.basename(item["attachment"]))
                        thumbpath = item["attachment"][item["attachment"].find("static"):].replace(base, base + "_thumb")
                        thumbpath = rpath[0:rpath.find("static")] + thumbpath[thumbpath.find("static"):]
                        os.remove(item["attachment"])
                        os.remove(thumbpath)
                    except:
                         pass
                self.db.execute("delete from quality_attachment where quality_id=%s and type=1",qid)
                for picitem in piclist:
                    self.db.execute("insert into quality_attachment (type,quality_id,describeinfo,attachment) value(%s,%s,%s,%s)",1,qid,picitem["describe"],picitem["path"])
                self.api_response(
                    {'status': 'success', 'message': '修改成功'})
        else:
            lastrowid = self.db.execute_lastrowid(
                "insert into quality_supplier (userid, type, name,identifiers,company,address,createtime)"
                    "value(%s, %s, %s, %s, %s, %s, %s)",
                    id,usertype,name,identifiers,compny,address ,int(time.time()))

            for picitem in piclist:
                self.db.execute("insert into quality_attachment (type,quality_id,describeinfo,attachment) value(%s,%s,%s,%s)",1,lastrowid,picitem["describe"],picitem["path"])
            self.api_response(
                {'status': 'success', 'message': '提交成功'})
        pass

class QualityUploadHandler(BaseHandler):
    def get(self):
        pass

    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        quality=self.db.get("select id from quality_supplier where userid=%s",id)
        if quality==None:
            self.api_response(
                {'status': 'fail', 'message': '请先认证'})
            return
        qid=quality.id
        imgtype=self.get_argument("imgtype",None)
        imglist=[]
        for i in range(1,100):
            img =self.get_argument("pic%s"%i,None)
            if img==None:
                break
            if img=="":#为空意味删除
                continue
            rpath = config.img_path
            path = rpath[0:rpath.find("static")] + img[img.find("static/"):]  # 服务器绝对路径
            desc=self.get_argument("descpic%s"%i,"")
            varietyname=self.get_argument("varietypic%s"%i,"")
            item={"path":path,"describe":desc,"varietyname":varietyname}
            imglist.append(item)

        attachments = self.db.query("select * from quality_attachment where quality_id=%s and type=%s", qid,imgtype)
        plist = [item["path"] for item in imglist]
        for item in attachments:  # 删除不要的图片文件
            if item["attachment"] in plist:
                continue
            try:
                rpath = config.img_path
                base, ext = os.path.splitext(os.path.basename(item["attachment"]))
                thumbpath = item["attachment"][item["attachment"].find("static"):].replace(base, base + "_thumb")
                thumbpath = rpath[0:rpath.find("static")] + thumbpath[thumbpath.find("static"):]
                os.remove(item["attachment"])
                os.remove(thumbpath)
            except:
                pass
        self.db.execute("delete from quality_attachment where quality_id=%s and type=%s", qid,imgtype)

        for picitem in imglist:
            self.db.execute(
                "insert into quality_attachment (type,quality_id,describeinfo,attachment,varietyname) value(%s,%s,%s,%s,%s)",imgtype, qid,
                picitem["describe"], picitem["path"],picitem["varietyname"])
        self.api_response(
            {'status': 'success', 'message': '提交成功'})


class UpdateRecordHandler(BaseHandler):
    def get(self):
        pass

    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        user=self.db.get("select * from users where id=%s",id)
        if user==None:
            self.api_response(
                {'status': 'fail', 'message': '没有该用户'})
            return
        recordlist=[]
        for i in range(1,100):#暂时存100条
            recordtime=self.get_argument("recordtime%s"%i,"")
            if recordtime=="":
                continue
            recorder=self.get_argument("recorder%s"%i,"")
            contacttype=self.get_argument("contacttype%s"%i,"")
            abstract=self.get_argument("abstract%s"%i,"")
            item={"recordtime":recordtime,"recorder":recorder,"contacttype":contacttype,"abstract":abstract}
            recordlist.append(item)
        self.db.execute("delete from follow_record where userid=%s", id)

        for record in recordlist:
            self.db.execute(
                "insert into follow_record (recorder,contacttype,abstract,recordtime,userid,createtime) value(%s,%s,%s,%s,%s,%s)",record["recorder"], record["contacttype"],
                record["abstract"], record["recordtime"],id,str(int(time.time())))
        self.api_response({'status': 'success', 'message': '提交成功'})

class UpgradeUserHandler(BaseHandler):
    def get(self):
        pass

    @tornado.web.authenticated
    def post(self):
        id = self.get_argument("id", None)
        user=self.db.get("select * from users where id=%s",id)
        if user==None:
            self.api_response(
                {'status': 'fail', 'message': '没有该用户'})
            return
        membertype=self.get_argument("membertype", None)
        term=self.get_argument("term", None)
        upgradetime=int(time.time())
        expiredday=datetime.now()+timedelta(days=int(term)*365)
        expiredtime=int(time.mktime(expiredday.timetuple()))
        if membertype and term:
            member=self.db.get("select * from member where userid=%s",id)
            if member:
                self.db.execute("update member set term=%s,upgradetime=%s,type=%s,expiredtime=%s where id=%s",term,upgradetime,membertype,expiredtime,member.id)
            else:
                self.db.execute("insert into member (userid,term,upgradetime,type,expiredtime) value(%s,%s,%s,%s,%s)",id, term, upgradetime,
                                membertype, expiredtime)
        self.api_response({'status': 'success', 'message': '提交成功'})

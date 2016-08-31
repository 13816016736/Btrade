# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import json, os, datetime
from utils import *
from config import *
import random
import time
from collections import defaultdict
from webbasehandler import purchase_push_trace
import logging
from mongodb import PymongoDateBase

class QuoteHandler(BaseHandler):

    @purchase_push_trace
    @tornado.web.authenticated
    def get(self, purchaseinfoid):
        #purchaseinfo = self.db.get("select t.*,a.position from (select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,"
        #"p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.term,p.status,p.areaid,p.invoice,pi.id pid,"
        #"pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specification,pi.views from purchase p,purchase_info pi "
        #"where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid", purchaseinfoid)


        #获取采购单信息
        purchaseinfo = self.db.get(
            "select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,"
            "p.term,p.status,p.areaid,p.invoice,pi.id pid,pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specification,"
            "pi.views,pi.shine from purchase p,purchase_info pi where p.id = pi.purchaseid and pi.id = %s", purchaseinfoid)

        # 获取采购单area信息
        areaid = purchaseinfo["areaid"]
        areainfo = self.db.get("select position from area where id =%s", areaid)
        if areainfo:
            purchaseinfo["position"] = areainfo.position
        else:
            purchaseinfo["position"] =""


        # 判断用户状态以及采购单是否为阳光速配
        if purchaseinfo["shine"]==1:
            member = self.db.get("select * from member where userid = %s and type=2 and status=1", self.session.get("userid"))
            if member==None:#未开通供货商阳光速配
                self.redirect('/sunshine/?pid=%s'%purchaseinfoid)
                return


        #获得采购品种图片
        attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", purchaseinfoid)
        for attachment in attachments:
            base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
            attachment["attachment"] = config.img_domain+attachment["attachment"][attachment["attachment"].find("static"):].replace(base, base+"_thumb")
        purchaser = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
        purchaseinfo["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(purchaseinfo["createtime"])))
        if purchaseinfo["term"] != 0:
            purchaseinfo["expire"] = datetime.datetime.fromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
            purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
        purchaseinfo["attachments"] = attachments

        childs = []
        # 判断是否是主账号
        parent = self.db.query("select * from child_user where parent_user_id=%s", purchaser["id"])
        if parent:
            # 取所有子账号id
            for item in parent:
                childs.append(str(item["child_user_id"]))
        else:
            # 判断是否是子账号
            maxNum = 0  # 主账号的子账号最大数目
            maxParent = None
            childids = self.db.query("select * from child_user where child_user_id=%s", purchaser["id"])
            if childids:
                for c in childids:
                    parentids = self.db.query("select * from child_user where parent_user_id=%s", c["parent_user_id"])
                    if len(parentids) > maxNum:
                        maxNum = len(parentids)
                        maxParent = parentids
            if maxParent:
                # 取所有子账号id
                for item in maxParent:
                    childs.append(str(item["child_user_id"]))

        childs.append(str(purchaser["id"]))


        #此采购商成功采购单数
        purchases = self.db.execute_rowcount("select * from purchase where userid in(%s)"%",".join(childs))
        #此采购单报价数
        quotes = self.db.execute_rowcount("select * from quote where purchaseinfoid = %s", purchaseinfoid)
        #此采购商回复供应商比例
        purchaser_quotes = self.db.query("select p.id,p.userid,t.state state from purchase p left join "
            "(select pi.purchaseid,q.state from purchase_info pi left join quote q on pi.id = q.purchaseinfoid) t "
                "on p.id = t.purchaseid where p.userid in(%s)"%",".join(childs))

        reply = 0
        print purchaser_quotes
        for purchaser_quote in purchaser_quotes:
            if purchaser_quote.state is not None and purchaser_quote.state != 0:
                reply = reply + 1

        accept = 0
        accept_quantity = 0
        accept_price = 0
        if purchases != 0:
            purchasesinfos = self.db.query(
                    "select pi.id,pi.quantity,pi.unit from purchase p  left join purchase_info pi on p.id=pi.purchaseid where p.userid in(%s) " % ",".join(
                        childs))
            purchasesinfomap = dict((i.id, [i.quantity, i.unit]) for i in purchasesinfos)
            purchaseinfoids = [str(i.id) for i in purchasesinfos]
            accept_purchaseinfos = self.db.query(
                    "select purchaseinfoid,price from quote where purchaseinfoid in(%s) and state=1 group by purchaseinfoid ORDER BY price  " % ",".join(
                        purchaseinfoids))
            accept = len(accept_purchaseinfos)
            for item in accept_purchaseinfos:
                unit = purchasesinfomap[item["purchaseinfoid"]][1]
                quantity = purchasesinfomap[item["purchaseinfoid"]][0]
                price = item["price"]
                if unit == u"公斤":
                    accept_quantity += int(quantity) / 1000
                    accept_price += int(quantity) * float(price)

                elif unit == u"吨":
                    accept_quantity += int(quantity)
                    accept_price += int(quantity) * float(price) * 1000
        quoteaccept = self.db.query(
                "select u.name,q.createtime from quote q  left join users u on q.userid=u.id where q.purchaseinfoid=%s order by q.createtime desc",
            purchaseinfoid)
        for item in quoteaccept:
            item["createtime"] = time.strftime("%m-%d %H:%M", time.localtime(float(item["createtime"])))

        #本周可报价次数
        t = time.time()
        week_begin = get_week_begin(t,0)
        week_end = get_week_begin(t,1)
        quotecount = self.db.execute_rowcount("select id from quote where userid = %s and createtime > %s and createtime < %s"
                                 , self.session.get("userid"), week_begin,week_end)
        memberinfo=self.db.get("select id from member where type in(1,2) and userid=%s and status=1",self.session.get("userid"))
        factor=1
        if memberinfo:
            factor=10
        quotechances = config.conf['QUOTE_NUM']*factor - quotecount if config.conf['QUOTE_NUM']*factor - quotecount > 0 else 0

        #获取图片
        uploadfiles = self.session.get("uploadfiles_quote", {})
        for k in uploadfiles:
            base, ext = os.path.splitext(os.path.basename(uploadfiles[k]))
            uploadfiles[k] = config.img_domain+uploadfiles[k][uploadfiles[k].find("static"):].replace(base, base+"_thumb")

        self.render("quote.html", purchaser=purchaser, purchase=purchaseinfo, purchases=purchases, quotes=quotes,
                    reply=int((float(reply)/float(len(purchaser_quotes))*100) if len(purchaser_quotes) != 0 else 0),
                    uploadfiles=uploadfiles, quotechances=quotechances,accept=accept,
                    accept_quantity=accept_quantity,accept_price=int(accept_price/10000),quoteaccept=quoteaccept)

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        logging.info("start post quote")
        purchaseinfoid = self.get_argument("purchaseinfoid")
        #验证对X采购单报价
        if purchaseinfoid == "":
            self.api_response({'status':'fail','message':'请选择采购单进行报价'})
            return
        quality = self.get_argument("quality")
        price = self.get_argument("price")
        #验证表单信息,货源描述,价格,价格说明
        if quality == "" or price == "":
            self.api_response({'status':'fail','message':'请完整填写'})
            return
        #至少上传一张图片
        uploadfiles = self.session.get("uploadfiles_quote")
        if len(uploadfiles) == 0:
            self.api_response({'status':'fail','message':'至少上传一张图片'})
            return
        #本周可报价次数
        t = time.time()
        week_begin = get_week_begin(t,0)
        week_end = get_week_begin(t,1)
        quotecount = self.db.execute_rowcount("select id from quote where userid = %s and createtime > %s and createtime < %s"
                                 , self.session.get("userid"), week_begin,week_end)
        memberinfo=self.db.get("select id from member where type in(1,2) and userid=%s and status=1",self.session.get("userid"))
        factor=1
        if memberinfo:
            factor=10
        if (config.conf['QUOTE_NUM']*factor - quotecount) < 0:
            self.api_response({'status':'fail','message':'本周已用完%s次报价机会,无法再进行报价'%(config.conf['QUOTE_NUM']*factor)})
            return
        #一个用户只能对同一个采购单报价一次
        quote = self.db.get("select id from quote where userid = %s and purchaseinfoid = %s and state = 0", self.session.get("userid"), purchaseinfoid)
        if quote is not None:
            self.api_response({'status':'fail','message':'您已经对次采购单进行过报价,无法再次报价'})
            return
        #不能对自己的采购单进行报价
        purchase = self.db.get("select t.*,u.name uname,u.phone,u.openid,u.openid2 from (select p.userid,p.term,p.createtime,pi.name,pi.varietyid,pi.specification,pi.quantity,pi.unit from purchase_info pi,purchase p where p.id = pi.purchaseid and pi.id = %s) "
                               "t left join users u on u.id = t.userid", purchaseinfoid)
        if purchase["userid"] == self.session.get("userid"):
            self.api_response({'status':'fail','message':'不能对自己的采购单进行报价'})
            return
        #报价结束不能报价
        if purchase["term"] != 0:
            purchase["expire"] = datetime.datetime.fromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
            if (purchase["expire"] - datetime.datetime.now()).days <= 0:
                self.api_response({'status':'fail','message':'此采购单报价已结束，无法再进行报价'})
                return

        today = time.time()
        quoteid = self.db.execute_lastrowid("insert into quote(userid,purchaseinfoid,quality,price,`explain`,createtime)value"
                                            "(%s,%s,%s,%s,%s,%s)", self.session.get("userid"),self.get_argument("purchaseinfoid"),
                                            quality,price,self.get_argument("explain"),
                                            int(today))
        #session加上quoteid:便于统计报价单状态
        logging.info("start set quoteid")
        self.session["quoteid"] = quoteid
        self.session.save()

        #为供货商积分：
        self.db.execute("update users set pushscore=pushscore+1 where id=%s",self.session.get("userid"))

        #保存session上传图片的路径
        if uploadfiles:
            for key in uploadfiles:
                self.db.execute("insert into quote_attachment (quoteid, attachment, type)value(%s, %s, %s)", quoteid, uploadfiles[key], key)
            uploadfiles = {}
            self.session["uploadfiles_quote"] = uploadfiles
            self.session.save()



        #给采购商发送通知
        #获得采购商userid
        quoter = self.db.get("select name,phone,openid,varietyids from users where id = %s", self.session.get("userid"))
        title = quoter["name"].encode('utf-8') + "对【" + purchase["name"].encode('utf-8') + "】提交了报价，立即处理"

        self.db.execute("insert into notification(sender,receiver,type,title,content,status,createtime)value(%s, %s, %s, %s, %s, %s, %s)",
                        self.session.get("userid"),purchase["userid"],2,title,self.get_argument("purchaseinfoid"),0,int(time.time()))

        #为报价者增加关注品种
        attention=[]
        if quoter["varietyids"]!="":
            attention=quoter["varietyids"].split(",")
        if purchase["varietyid"] not in attention:
            attention.append(str(purchase["varietyid"]))
            try:
               self.db.execute("update users set varietyids = %s where id = %s", ",".join(attention),
                                 self.session.get("userid"))
            except Exception,ex:
                logging.error("inser variety error %s",str(ex))



        #发短信通知采购商有用户报价
        quoteSms(purchase["phone"], purchase["name"], quoter["name"], price, config.unit)
        #发微信模板消息通知采购商有用户报价
        quoteWx(purchase["openid"], purchaseinfoid, purchase["name"], quoter["name"], price, purchase["unit"], quality, today)
        if purchase["openid2"]!="":
            quoteWx(purchase["openid2"], purchaseinfoid, purchase["name"], quoter["name"], price, purchase["unit"],
                    quality, today,2)
        #发微信模板消息提示报价的供应商报价成功啦
        quoteSuccessWx(quoter["openid"], purchase["uname"], purchase["name"], purchase["specification"], purchase["quantity"], price, purchase["unit"], quality, today)
        self.api_response({'status':'success','message':'请求成功'})

class QuoteUploadHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self, purchaseinfoid, type):
        #print purchaseinfoid
        print type
        self.render("uploads_pic.html", purchaseinfoid=purchaseinfoid, type=type)

    @tornado.web.authenticated
    def post(self):
        pass

class QuoteSuccessHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        pass

    @purchase_push_trace
    @tornado.web.authenticated
    def post(self):
        if self.session.get("uploadfiles_quote"):
            self.session["uploadfiles_quote"] = {}
            self.session.save()
        first = False
        purchaseinfoid = self.get_argument("purchaseinfoid", None)
        if purchaseinfoid:
            count = self.db.execute_rowcount("select id from quote where purchaseinfoid = %s", purchaseinfoid)
            if count == 1:
                first = True

        ua = self.request.headers['User-Agent']
        purchaseinfonum = self.db.execute_rowcount("select id from purchase_info where status!=0")
        if ua.lower().find("micromessenger") != -1:
            self.redirect(
                    "/checkfans?state=quotesuccess")
        else:
            self.render("quote_success_C.html", purchaseinfonum=purchaseinfonum)



class WeixinHandler(BaseHandler):

    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        self.render("weixin.html")

    @tornado.web.authenticated
    def post(self):
        pass

class QuoteDetailHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self, quoteid, nid):
        quote = self.db.get("select * from quote where id = %s", quoteid)
        quote["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(quote["createtime"])))
        quoteattachment = self.db.query("select * from quote_attachment where quoteid = %s", quoteid)
        for qa in quoteattachment:
            base, ext = os.path.splitext(os.path.basename(qa["attachment"]))
            qa["attachment"] = config.img_domain+qa["attachment"][qa["attachment"].find("static"):].replace(base, base+"_thumb")

        #查询采购单信息
        #purchaseinfo = self.db.get("select t.*,a.position from "
        #"(select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.term,p.status,p.areaid,p.invoice,pi.id pid,"
        #"pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specification,pi.views from purchase p,purchase_info pi "
        #"where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid", quote["purchaseinfoid"])

        # 获取采购单信息
        purchaseinfo = self.db.get(
            "select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,"
            "p.term,p.status,p.areaid,p.invoice,pi.id pid,pi.name,pi.price,pi.quantity,pi.unit,pi.quality,pi.origin,pi.specification,"
            "pi.views from purchase p,purchase_info pi where p.id = pi.purchaseid and pi.id = %s", quote["purchaseinfoid"])

        # 获取采购单area信息
        areaid = purchaseinfo["areaid"]
        areainfo = self.db.get("select position from area where id =%s", areaid)
        if areainfo:
            purchaseinfo["position"] = areainfo.position
        else:
            purchaseinfo["position"]=""




        quote["unit"] = purchaseinfo["unit"]

        #获得采购品种图片
        attachments = self.db.query("select * from purchase_attachment where purchase_infoid = %s", quote["purchaseinfoid"])
        for attachment in attachments:
            base, ext = os.path.splitext(os.path.basename(attachment["attachment"]))
            attachment["attachment"] = config.img_domain+attachment["attachment"][attachment["attachment"].find("static"):].replace(base, base+"_thumb")
        user = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
        purchaseinfo["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(purchaseinfo["createtime"])))
        if purchaseinfo["term"] != 0:
            purchaseinfo["expire"] = datetime.datetime.fromtimestamp(float(purchaseinfo["createtime"])) + datetime.timedelta(purchaseinfo["term"])
            purchaseinfo["timedelta"] = (purchaseinfo["expire"] - datetime.datetime.now()).days
        purchaseinfo["attachments"] = attachments

        others = self.db.query("select id from purchase_info where purchaseid = %s and id != %s",
                                      purchaseinfo["id"], purchaseinfo["pid"])

        #此采购商成功采购单数
        purchases = self.db.execute_rowcount("select * from purchase where userid = %s and status = 4", user["id"])
        #此采购单报价数
        quotes = self.db.query("select * from quote where purchaseinfoid = %s", purchaseinfo["pid"])
        acceptuserid = []
        for q in quotes:
            if q.state == 1:
                acceptuserid.append(str(q.userid))
        acceptuser = []
        if acceptuserid:
            acceptuser = self.db.query("select nickname from users where id in (" + ",".join(acceptuserid) + ")")
        #此采购商回复供应商比例
        purchaser_quotes = self.db.query("select p.id,p.userid,t.state state from purchase p left join "
            "(select pi.purchaseid,q.state from purchase_info pi left join quote q on pi.id = q.purchaseinfoid) t "
                "on p.id = t.purchaseid where p.userid = %s", user["id"])
        reply = 0

        for purchaser_quote in purchaser_quotes:
            if purchaser_quote.state is not None and purchaser_quote.state != 0:
                reply = reply + 1

        #报价回复消息标记为已读
        if int(nid) > 0:
            self.db.execute("update notification set status = 1 where receiver = %s and id = %s", self.session.get("userid"), nid)

        self.render("quote_detail.html", user=user, purchase=purchaseinfo, others=len(others), purchases=purchases,
                    quotes=quotes, acceptuser=acceptuser, reply=int((float(reply)/float(len(purchaser_quotes))*100) if len(purchaser_quotes) != 0 else 0),
                    quote=quote, quoteattachment=quoteattachment)

    @tornado.web.authenticated
    def post(self):
        pass

class QuoteListHandler(BaseHandler):
    @purchase_push_trace
    @tornado.web.authenticated
    def get(self):
        userid = self.session.get("userid")
        #获取我发出的报价信息
        #myquotes = self.db.query("select ta.*,n.id nid from (select mq.*,u.name uname,u.nickname,u.type,u.phone from "
        #                         "(select ta.*,p.createtime purchasetime,p.term,p.userid purchaseuserid from ("
        #                         "select q.*,pi.purchaseid,pi.name,pi.specification,pi.origin,pi.quantity,pi.unit "
        #                         "from quote q,purchase_info pi where q.purchaseinfoid = pi.id and q.userid = %s order by q.createtime desc"
        #                         ") ta,purchase p where ta.purchaseid = p.id) mq,users u where mq.purchaseuserid = u.id) ta "
        #                         "left join notification n on ta.userid = n.sender and n.content = ta.purchaseinfoid", userid)
        myquotes = self.db.query("select q.*,pi.purchaseid,pi.name,pi.specification,pi.origin,pi.quantity,pi.unit "
                                 "from quote q,purchase_info pi where q.purchaseinfoid = pi.id and q.userid = %s order by q.createtime desc",userid)#获取我的报价信息
        if myquotes:
            purchaseids= [str(quote["purchaseid"]) for quote in myquotes]
            purchaseinfoids=[str(quote["purchaseinfoid"]) for quote in myquotes]
            purchase =self.db.query("select id,createtime purchasetime,term,userid purchaseuserid from purchase where id in(%s)" %",".join(purchaseids))#获取报价的采购单信息
            purchasedict = dict((i.id, [i.purchasetime,i.term,i.purchaseuserid]) for i in purchase)
            userinfo = self.db.get(
                "select id,nickname,name,type,phone from users where id =%s ",userid)  # 获取user信息
            notification=self.db.query("select content as purchaseinfoid, id from notification where sender=%s and content in(%s)"%(userid,",".join(purchaseinfoids)))#获取该user的notification
            notificationdict = dict((i.purchaseinfoid, i.id) for i in notification)




        quoteids = []
        over = 0
        unreply = 0
        for myquote in myquotes:
            #拼接信息
            myquote["purchasetime"]=purchasedict[myquote["purchaseid"]][0]
            myquote["term"]=purchasedict[myquote["purchaseid"]][1]
            myquote["purchaseuserid"] = purchasedict[myquote["purchaseid"]][2]
            myquote["nickname"]=userinfo["nickname"]
            myquote["uname"] = userinfo["name"]
            myquote["type"]=userinfo["type"]
            myquote["phone"] = userinfo["phone"]
            myquote["nid"]= notificationdict.get(str(myquote.purchaseinfoid), None)



            quoteids.append(str(myquote.id))
            expire = datetime.datetime.fromtimestamp(float(myquote["purchasetime"])) + datetime.timedelta(myquote["term"])
            myquote["timedelta"] = (expire - datetime.datetime.now()).days
            myquote["datetime"] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(float(myquote["createtime"])))
            if myquote["timedelta"] <= 0:
                over =+ 1
            if myquote.state == 0:
                unreply =+ 1

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
        for mq in myquotes:
            if myquoteattachments.has_key(mq.id):
                mq["attachments"] = myquoteattachments[mq.id]
            else:
                mq["attachments"] = []

        self.render("quote_list.html", myquotes=myquotes, over=over, unreply=unreply)

    @tornado.web.authenticated
    def post(self):
        pass


class FeedBackHandler(BaseHandler):
    @purchase_push_trace
    def get(self):
        pass
    def post(self):
        uuid = self.session.get("uuid")
        userid=self.session.get("userid")
        content=self.get_argument("content","")
        pid=self.get_argument("pid","")
        if userid==None:
            userid=""
        if uuid==None:
            uuid=""
        mongodb = PymongoDateBase.instance().get_db()
        item={"uuid":uuid,"userid":userid,"content":content,"purchaseinfoid":pid,"createtime":int(time.time())}
        mongodb.feedback.insert(item)
        self.api_response({'status': 'success', 'message': '反馈成功'})


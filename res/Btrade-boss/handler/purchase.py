# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import json, os, datetime, random, time
from utils import *
from config import *
from collections import defaultdict
from urllib import urlencode
import tornado.gen
from pushengine.tasks import task_generate


class PurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, type=-1, starttime=0, endtime=0, page=0):
        query = self.get_argument("query", None)
        page=self.get_argument("page",0)
        type=self.get_argument("type",-1)
        starttime=self.get_argument("starttime","")
        endtime=self.get_argument("endtime","")
        page = (int(page) - 1) if page > 0 else 0
        #查询条件
        condition = []
        if int(type) >= 0:
            condition.append("p.status = "+type)
        if starttime !="" and endtime != "":
            condition.append("p.createtime > "+str(int(time.mktime(time.strptime(starttime,'%Y-%m-%d %H:%M')))))
            condition.append("p.createtime < "+str(int(time.mktime(time.strptime(endtime,'%Y-%m-%d %H:%M')))))
        if query:
            varieties = self.db.query("select id from variety where name = %s", query)
            if len(varieties) == 1:
                p = self.db.query("select purchaseid from purchase_info where varietyid = %s", varieties[0]["id"])
                condition.append("p.id in ("+",".join([str(pur["purchaseid"]) for pur in p])+")")
        conditionstr = ""
        if condition:
            conditionstr = ("where "+(" and ".join(condition)))
        query_str={}
        query_str["type"]=type
        if starttime!="":
            query_str["starttime"]=starttime
        if endtime!="":
            query_str["endtime"] = endtime
        if query:
            query_str["query"]=query.encode('utf8')
        nav = {
            'model': 'purchase/purchaselist',
            'cur': page + 1,
            'num': self.db.execute_rowcount("select id from purchase p "+conditionstr),
            'query': "%s" % urlencode(query_str),
        }

        purchaseinf = defaultdict(list)
        purchases=self.db.query("select p.*,u.nickname,u.name from purchase p left join users u on p.userid = u.id  %s"% conditionstr
                                   + " order by p.createtime desc limit %s,%s",page * config.conf['POST_NUM'], config.conf['POST_NUM'])

        #获取采购单的详细信息，包括user和area信息

        #purchases = self.db.query("select t.*,a.position from "
        #                          "(select p.*,u.nickname,u.name from purchase p left join users u on p.userid = u.id "+
        #                          conditionstr + " order by p.createtime desc limit %s,%s) t "
        #                          "left join area a on t.areaid = a.id", page * config.conf['POST_NUM'], config.conf['POST_NUM'])

        if purchases:
            areaids = [str(purchase["areaid"]) for purchase in purchases]
            areaids = list(set(areaids))  # 去重
            allpositions = self.db.query("select id,position from area where id in (%s)" % ",".join(areaids))
            positions = defaultdict(list)
            for item in allpositions:
                positions[item["id"]] = item["position"]
            for purchase in purchases:
                purchase["position"] = positions.get(purchase["areaid"])
            purchaseids = [str(purchase["id"]) for purchase in purchases]
            purchaseinfos = self.db.query("select p.*,q.id qid,count(q.id) quotecount,count(if(q.state=1,true,null )) intentions, count(if(q.state=0,true,null )) unread "
                                          "from purchase_info p left join quote q on p.id = q.purchaseinfoid where p.purchaseid in (%s) group by p.id"%",".join(purchaseids))
            #获取采购单报价信息
            purchaseinfoids = [str(purchaseinfo["id"]) for purchaseinfo in purchaseinfos]
            purchaseattachments = self.db.query("select * from purchase_attachment where purchase_infoid in ("+",".join(purchaseinfoids)+")")
            attachments = defaultdict(list)
            for attachment in purchaseattachments:
                attachments[attachment["purchase_infoid"]] = attachment
            for purchaseinfo in purchaseinfos:
                purchaseinfo["attachments"] = attachments.get(purchaseinfo["id"])
                purchaseinf[purchaseinfo["purchaseid"]].append(purchaseinfo)
        for purchase in purchases:
            purchase["purchaseinfo"] = purchaseinf.get(purchase["id"]) if purchaseinf.get(purchase["id"]) else []
            purchase["datetime"] = time.strftime("%Y-%m-%d %H:%M", time.localtime(float(purchase["createtime"])))
            if purchase["term"] != 0:
                purchase["expire"] = datetime.datetime.fromtimestamp(float(purchase["createtime"])) + datetime.timedelta(purchase["term"])
                purchase["timedelta"] = (purchase["expire"] - datetime.datetime.now()).days

        #统计采购单各状态的数量
        results = self.db.query("select status, count(*) count from purchase group by status")
        stat = {}
        for r in results:
            stat[r.status] = r.count
        self.render("purchase.html", purchases=purchases, nav=nav, stat=stat, type=type, starttime=starttime, endtime=endtime, query=query)

    def post(self):
        pass

class PurchaseInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, id):
        #获取单个采购单信息，包括user和area信息
        #purchaseinfo = self.db.get("select t.*,a.position from (select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,"
        #"p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.term,p.status,p.areaid,pi.id pid,"
        #"pi.name,pi.price,pi.quantity,pi.unit,pi.origin,pi.quality,pi.specification,pi.views from purchase p,purchase_info pi "
       # "where p.id = pi.purchaseid and pi.id = %s) t left join area a on a.id = t.areaid",id)

        purchaseinfo =self.db.get("select p.id,p.userid,p.pay,p.payday,p.payinfo,p.accept,"
        "p.send,p.receive,p.other,p.supplier,p.remark,p.createtime,p.term,p.status,p.areaid,pi.id pid,"
        "pi.name,pi.price,pi.quantity,pi.unit,pi.origin,pi.quality,pi.specification,pi.views,pi.status from purchase p,purchase_info pi "
        "where p.id = pi.purchaseid and pi.id = %s",id)


        ret = self.db.get("select position from area where id =%s",purchaseinfo["areaid"])
        if ret:
            purchaseinfo["position"]=ret.position
        else:
            purchaseinfo["position"] =""

        user = self.db.get("select * from users where id = %s", purchaseinfo["userid"])
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
            quotes = self.db.query("select q.*,u.name,u.nickname,u.phone from quote q left join users u on q.userid = u.id where q.purchaseinfoid = %s", id)
            quoteids = []
            if quotes:
                for quote in quotes:
                    quoteids.append(str(quote.id))
                    quote["datetime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(quote["createtime"])))
                    quote["unit"] = purchaseinfo["unit"]
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
            self.render("purchaseinfo.html", user=user, purchase=purchaseinfo, quotes=quotes, others=len(others))
        else:
            self.error("此采购订单不属于你", "/purchase")

    def post(self):
        pass

class RemovePurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    def post(self):
        self.db.execute("UPDATE purchase SET status = 0 WHERE id = %s", self.get_argument("pid"))
        self.api_response({'status':'success','message':'请求成功'})

class PushPurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        #purchaseinfoid = self.get_argument("purchaseinfoid")
        #purchaser = self.get_argument("purchaser")#其实不需要这个参数
        #purchaseinfo = self.db.get("select pi.id purchaseinfoid,pi.varietyid,pi.name variety,pi.specification,pi.quantity,pi.unit,pi.quality,pi.origin,pi.pushcount,p.userid,p.createtime from purchase_info pi left join purchase p on pi.purchaseid = p.id where pi.id = %s", purchaseinfoid)
        #u = self.db.get("select name,nickname from users where id = %s", purchaseinfo["userid"])
        #purchaseinfo["name"] = u["name"]
        #purchaseinfo["nickname"] = u["nickname"]
        #users = self.db.query("select phone,openid from users where find_in_set(%s,varietyids)", purchaseinfo["varietyid"])
        #yt = self.db.query("select mobile from supplier where find_in_set(%s,variety) and mobile != '' and pushstatus=1", purchaseinfo["varietyid"])
        #phones = set()
        #openids = set()
        #for i in users:
        #    phones.add(i["phone"])
        #    openids.add(i["openid"])
        #for j in yt:
        #    phones.add(j["mobile"])
        #phones = list(set(phones))
        #phones =["13638654365"]
        #openids=["oTEeNweXKZh8FXoP3Fwu_y3AGPkk"]
        #if phones:
        #    #测试先不发送信息，只保存信息到mongodb
        #   push_user_infos = []
        #    uuidmap={}
        #    createtime = int(time.time())
        #    quote = 0  # 0,未报价，1，已报价
        #    sendstatus = 0  # 0,未发送，1:发送成功,2:失败

        #    mongodb =  PymongoDateBase.instance().get_db()
        #    colleciton= mongodb.transform_rate
        #    push_phone_id=colleciton.insert({"purchaseinfoid":purchaseinfoid ,"order":int(purchaseinfo["pushcount"])+1,"quote":"","type":1,"createtime":createtime})
        #    push_wx_id=colleciton.insert({"purchaseinfoid":purchaseinfoid ,"order":int(purchaseinfo["pushcount"])+1,"quote":"","type":2,"createtime":createtime})

        #    for phone in phones:
        #        uuid = md5(str(time.time())+ str(phone))[8:-8]
        #        sendid = phone
        #        createtime = int(time.time())
        #        push_user = {"pushid":push_phone_id ,"uuid":uuid,"createtime":createtime,"click":0,"sendid":sendid,"sendstatus":sendstatus,"type":1}
        #        push_user_infos.append(push_user)
        #        uuidmap[sendid]=uuid
        #    for openid in  openids:
        #        uuid = md5(str(time.time()) + str(openid))[8:-8]
        #        sendid = openid
        #        createtime = int(time.time())
        #        push_user = {"pushid":push_wx_id ,"uuid": uuid, "createtime": createtime,"click":0, "sendid": sendid,"sendstatus":sendstatus,"type":2}
        #        push_user_infos.append(push_user)
        #        uuidmap[sendid] = uuid

        #    colleciton = mongodb.push_record
        #    colleciton.insert_many(push_user_infos)

         #   logger = logging.getLogger()
        #    logger.info("pushPurchase start thread,phone=%s,purchaseinfo=%s,uuidmap=%s",phones, purchaseinfo,uuidmap)
        #    thread.start_new_thread(pushPurchase, (phones, purchaseinfo,uuidmap))
        #    thread.start_new_thread(pushPurchaseWx, (openids, purchaseinfo,uuidmap))
        #    self.db.execute("update purchase_info set pushcount=%s where id=%s",int(purchaseinfo["pushcount"])+1, purchaseinfoid)

            #pushPurchase(phones, purchaseinfo)
            #pushPurchaseWx(openids, purchaseinfo)

        #生成celery任务，只要发送任务id
        purchaseinfoid = self.get_argument("purchaseinfoid")
        task={"purchaseinfoid":purchaseinfoid,"tasktype":1,"channel":1}
        task_generate.apply_async(args=[task])
        task={"purchaseinfoid":purchaseinfoid,"tasktype":1,"channel":2}
        task_generate.apply_async(args=[task])

        self.api_response({'status':'success','message':'推送成功'})
        #else:
        #self.api_response({'status':'fail','message':'暂无关注此品种的用户'})

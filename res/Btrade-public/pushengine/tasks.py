# -*- coding:utf-8 -*-
# tasks.py
from __future__ import absolute_import
from pushengine.celery import celerysever
from mongodb import PymongoDateBase
from database import database
from kafkaserver.producer import KafkaProduceServer
from globalconfig import *
from pushengine.engineconfig import *
import pymongo
from datetime import timedelta,datetime
import time


#任务
@celerysever.task
def task_generate(task):#生成发送任务
    mongodb = PymongoDateBase.instance().get_db()
    sqldb = database.instance().get_session()
    tasktype=task["tasktype"]
    purchaseinfoid = task["purchaseinfoid"]
    channel = task["channel"]
    record = mongodb.celery_task.find(
        {"purchaseinfoid": purchaseinfoid, "channel": channel, "tasktype": tasktype}).sort("order", pymongo.DESCENDING)
    if record.count() == 0:
        order = 1
    else:
        order = record[0]["order"] + 1
    purchaseinfo = sqldb.get(
        "select pi.id purchaseinfoid,pi.varietyid,p.userid uid from purchase_info pi left join purchase p on pi.purchaseid = p.id where pi.id = %s",
        purchaseinfoid)
    if tasktype==1:
        sendids = set()
        filtersend = []
        if order>max_push_time:
            return
        if order!=1:#不是第一次发送，过滤发送过的
            records = mongodb.transform_rate.find({"purchaseinfoid": purchaseinfoid, "type": channel})
            for item in records:
                pushrecord= mongodb.push_record.find({"pushid": item["_id"]})
                for item in pushrecord:
                    filtersend.append(item["sendid"])
        if channel == 1:
            #短信渠道
            phonecondition = ""
            filtersend = [str(i) for i in filtersend]
            if filtersend != []:
                phonecondition = " and phone not in(%s)" % ",".join(filtersend)
            task = {"purchaseinfoid": purchaseinfoid, "tasktype": tasktype, "channel": 1, "order": order,
                        "status": 0,"createtime":int(time.time())}
            userphones = sqldb.query(
                    "select phone from users where find_in_set(%s,varietyids)" + phonecondition + " order by pushscore  limit 0,%s",
                    purchaseinfo["varietyid"], max_wx_num)
            if filtersend != []:
                phonecondition = " and mobile not in(%s)" % ",".join(filtersend)
            yt = sqldb.query(
                    "select mobile from supplier where find_in_set(%s,variety) and mobile != '' and pushstatus=1" + phonecondition + " order by pushscore  limit 0, %s",
                    purchaseinfo["varietyid"], max_phone_num)
            for i in userphones:
                sendids.add(str(i["phone"]))
            for j in yt:
                sendids.add(str(j["mobile"]))
            sendids = list(set(sendids))
            print sendids
        elif channel==2:
            #微信渠道
            wxcondition=""
            filtersend = ["'"+str(i)+"'" for i in filtersend]
            if filtersend!=[]:
                 wxcondition = " and openid not in(%s)" % ",".join(filtersend)
            task = {"purchaseinfoid": purchaseinfoid, "tasktype": tasktype, "channel": 2, "order": order,
                        "status": 0,"createtime":int(time.time())}
            userwxs = sqldb.query(
                    "select openid from users where find_in_set(%s,varietyids) and openid!=''" + wxcondition + " order by pushscore limit 0,%s",
                    purchaseinfo["varietyid"], max_wx_num)
            for i in userwxs:
                    sendids.add(str(i["openid"]))
            sendids = list(set(sendids))
            print sendids
        if len(sendids) != 0:
            taskid = mongodb.celery_task.insert(task)
            taskinfo = {"taskid": taskid, "sendlist": ",".join(sendids)}
            collection = mongodb.celery_task_info
            collection.insert(taskinfo)
            sendkafka.apply_async(args=[taskid])
    else:
        #提醒采购商
        if order!=1:
            if order>max_notify_time or (int(time.time())-int(record["createtime"]))<notify_days*24*60*60:
                return

        sendid=""
        if channel==1:
            userphone=sqldb.get("select id,phone from users where id=%s",purchaseinfo["uid"])
            if userphone:
                sendid=userphone["phone"]
        elif channel==2:
            useropenid=sqldb.get("select id,openid from users where id=%s",purchaseinfo["uid"])
            if useropenid:
                sendid=useropenid["openid"]
        if sendid!="":
            task = {"purchaseinfoid": purchaseinfoid, "tasktype": tasktype, "channel": channel, "order": order,
                    "status": 0, "createtime": int(time.time())}
            taskid = mongodb.celery_task.insert(task)
            taskinfo = {"taskid": taskid, "sendlist": sendid}
            collection = mongodb.celery_task_info
            collection.insert(taskinfo)
            sendkafka.apply_async(args=[taskid])
        pass



#发的kafka上执行
@celerysever.task
def sendkafka(taskid):
    producer_server = KafkaProduceServer(send_task_topic, kafka_server)
    producer_server.sendJson("data", {"taskid":str(taskid),"messagetype": 2})
    producer_server.close()
    pass


#调度器
@celerysever.task
def analysis_record():#每天九点定时检测
   mongodb = PymongoDateBase.instance().get_db()
   sqldb = database.instance().get_session()
   #items =mongodb.transform_rate.find()#检测发送超过一天的统计记录 条件通过createtime
   yesterday = datetime.now() - timedelta(days=1)
   timeStamp = time.mktime(yesterday.timetuple())
   func = '''
      function(obj,prev){
      if (obj.order>prev.latest_order){
            prev.latest_order=obj.order
            prev.latest_id=obj._id
            }
        }
      '''
   ret = mongodb.transform_rate.group(['purchaseinfoid','type'], {"createtime":{"$gt":int(timeStamp)}}, {"latest_order": 0, "latest_id": ""}, func)
   for item in ret :
       print item
       id=item["latest_id"]
       transform=mongodb.transform_rate.find_one({"_id":id})
       type=transform["type"]
       order=transform["order"]
       if order > max_push_time:
           continue
       purchaseinfoid=transform["purchaseinfoid"]
       quote_count =0
       if transform["quote"]!="":
            quote_count=len(transform["quote"].split(","))
       push_count=mongodb.push_record.find({"pushid":id}).count()
       if push_count!=0:
            click_count=mongodb.push_record.find({"pushid":id,"click":{'$gt':0}}).count()
            reject_rate=1
            if quote_count!=0:
                aject = sqldb.query("select id from quote where id in(%s) and state=2" % transform["quote"])
                quote_aject_count = len(aject)
                reject_rate=quote_aject_count/(quote_count*1.0)
            if click_count/(push_count*1.0)<click_rate or quote_count/(push_count*1.0)<quote_rate or reject_rate>reject_quote_rate :
                task = {"purchaseinfoid": purchaseinfoid, "tasktype": 1,"channel":type}
                task_generate.apply_async(args=[task])




@celerysever.task
def analysis_notify():#每天九点价回复情况，生成提醒
    sqldb = database.instance().get_session()
    ret=sqldb.query("select id from purchase_info where status=0")
    for item in ret:
        purchaseinfoid=item["id"]
        ret=sqldb.query("select id from quote where purchaseinfoid =%s" ,purchaseinfoid)
        quote_num=len(ret)
        if quote_num!=0:
            ret=sqldb.query("select id from quote where purchaseinfoid =%s and state!=0" , purchaseinfoid)
            reply_num=len(ret)
            if reply_num!=0:
                ret=sqldb.query("select id,createtime from quote where purchaseinfoid =%s order by createtime" , purchaseinfoid)
                latest_time=ret[0]["createtime"]
                if (int(time.time())-int(latest_time))>notify_days*24*60*60:
                    print purchaseinfoid
                    if reply_num/(quote_num*1.0)<reply_rate:
                        task = {"purchaseinfoid": purchaseinfoid, "tasktype": 2,"channel":1}
                        print task
                        task_generate.apply_async(args=[task])
                        task = {"purchaseinfoid": purchaseinfoid, "tasktype": 2,"channel":2}
                        print task
                        task_generate.apply_async(args=[task])




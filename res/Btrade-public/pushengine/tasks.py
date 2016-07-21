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



#任务
@celerysever.task
def task_generate(task):#生成发送任务
    mongodb = PymongoDateBase.instance().get_db()
    tasktype=task["tasktype"]
    if tasktype==1:
        purchaseinfoid=task["purchaseinfoid"]
        channel=task["channel"]
        record=mongodb.celery_task.find({"purchaseinfoid":purchaseinfoid,"channel":channel}).sort("order",pymongo.DESCENDING)
        if record.count()==0:
            order=1
        else:
            order=record[0]["order"]+1
        sqldb = database.instance().get_session()
        purchaseinfo = sqldb.get(
            "select pi.id purchaseinfoid,pi.varietyid from purchase_info pi left join purchase p on pi.purchaseid = p.id where pi.id = %s",
            purchaseinfoid)
        sendids = set()
        filtersend = []
        if order>max_push_time:
            return
        if order!=1:#不是第一次发送，过滤发送过的
            records = mongodb.celery_task.find({"purchaseinfoid": purchaseinfoid, "channel": channel})
            for item in records:
                taskinfo = mongodb.celery_task_info.find_one({"taskid": item["_id"]})
                if taskinfo:
                    phones = taskinfo["sendlist"].split(",")
                    filtersend = list(set(filtersend) ^ set(phones))
        if channel == 1:
            #短信渠道
            phonecondition = ""
            filtersend = [str(i) for i in filtersend]
            if filtersend != []:
                phonecondition = " and phone not in(%s)" % ",".join(filtersend)
            task = {"purchaseinfoid": purchaseinfoid, "tasktype": tasktype, "channel": 1, "order": order,
                        "status": 0}
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
                        "status": 0}
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
def analysis_record():#定时执行不停检测发送记录，超过一天分析是否重发
   mongodb = PymongoDateBase.instance().get_db()
   #items =mongodb.transform_rate.find()#检测发送超过一天的统计记录 条件通过createtime
   func = '''
      function(obj,prev){
      if (obj.order>prev.latest_order){
            prev.latest_order=obj.order
            prev.latest_id=obj._id
            }
        }
      '''
   ret = mongodb.transform_rate.group(['purchaseinfoid','type'], None, {"latest_order": 0, "latest_id": ""}, func)
   for item in ret :
       id=item["latest_id"]
       transform=mongodb.transform_rate.find_one({"_id":id})
       type=transform["type"]
       purchaseinfoid=transform["purchaseinfoid"]
       quote_count =0
       if transform["quote"]!="":
            quote_count=len(transform["quote"].split(","))
       push_count=mongodb.push_record.find({"pushid":id}).count()
       if push_count!=0:
            click_count=mongodb.push_record.find({"pushid":id,"click":{'$gt':0}}).count()
            print click_count,quote_count
            reject_rate=1
            if quote_count!=0:
                sqldb = database.instance().get_session()
                aject = sqldb.query("select * from quote where id in(%s) and state=2" % transform["quote"])
                quote_aject_count = len(aject)
                print quote_aject_count
                reject_rate=quote_aject_count/(quote_count*1.0)
            if click_count/(push_count*1.0)<click_rate or quote_count/(push_count*1.0)<quote_rate or reject_rate>reject_quote_rate :
                task = {"purchaseinfoid": purchaseinfoid, "tasktype": 1,"channel":type}
                task_generate.apply_async(args=[task])




@celerysever.task
def analysis_notify():#定时检测报价回复情况，生成提醒
    mongodb = PymongoDateBase.instance().get_db()
    func = '''
       function(obj,prev){
         prev.all_qutote=prev.all_qutote+","+obj.quote
         }
       '''
    ret = mongodb.transform_rate.group(['purchaseinfoid'], None, {"all_qutote": "", "latest_id": ""}, func)
    pass


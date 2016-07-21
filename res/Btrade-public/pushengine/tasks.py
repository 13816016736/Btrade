# -*- coding:utf-8 -*-
# tasks.py
from __future__ import absolute_import
from pushengine.celery import celerysever
from mongodb import PymongoDateBase
from database import database
from kafkaserver.producer import KafkaProduceServer
from globalconfig import *
from pushengine.engineconfig import *



#任务
@celerysever.task
def task_generate(task):#生成发送任务
    print task
    mongodb = PymongoDateBase.instance().get_db()
    tasktype=task["tasktype"]
    if tasktype==1:
        purchaseinfoid=task["purchaseinfoid"]
        tasktype=task["tasktype"]
        order=task["order"]
        filterphones = []
        filterwxs = []
        print order<max_push_time
        if order!=1 and order<max_push_time:#不是第一次发送，过滤发送过的
            #过滤短信的
            records=mongodb.celery_task.find({"purchaseinfoid": purchaseinfoid,"channel":1})
            for item in records:
                taskinfo=mongodb.celery_task_info.find_one({"taskid":item["_id"]})
                if taskinfo:
                    phones=taskinfo["sendlist"].split(",")
                    filterphones = list(set(filterphones) ^ set(phones))
            #过滤微信的
            records = mongodb.celery_task.find({"purchaseinfoid": purchaseinfoid, "channel": 2})
            for item in records:
                wxtaskinfo = mongodb.celery_task_info.find_one({"taskid": item["_id"]})
                if wxtaskinfo:
                    wxs = wxtaskinfo["sendlist"].split(",")
                    filterwxs = list(set(filterwxs) ^ set(wxs))
        phonecondition=""
        filterphones=[str(i) for i  in filterphones]
        filterwxs=["'"+str(i)+"'" for i in filterwxs]
        if filterphones!=[]:
            phonecondition=" and phone not in(%s)"%",".join(filterphones)
        wxcondition=""
        if filterwxs!=[]:
           wxcondition = " and openid not in(%s)" % ",".join(filterwxs)
        print phonecondition,wxcondition
        sqldb = database.instance().get_session()
        purchaseinfo = sqldb.get(
                "select pi.id purchaseinfoid,pi.varietyid,pi.name variety,pi.specification,pi.quantity,pi.unit,pi.quality,pi.origin,pi.pushcount,p.userid,p.createtime from purchase_info pi left join purchase p on pi.purchaseid = p.id where pi.id = %s",
                purchaseinfoid)
        task = {"purchaseinfoid": purchaseinfoid, "tasktype": tasktype, "channel": 1, "order": order,"status":0}
        taskid = mongodb.celery_task.insert(task)
        userphones = sqldb.query(
                "select phone from users where find_in_set(%s,varietyids)"+phonecondition+" order by pushscore  limit 0,%s",
                purchaseinfo["varietyid"], max_wx_num)
        if filterphones!=[]:
            phonecondition=" and mobile not in(%s)"%",".join(filterphones)
        yt = sqldb.query("select mobile from supplier where find_in_set(%s,variety) and mobile != '' and pushstatus=1"+phonecondition+" order by pushscore  limit 0, %s", purchaseinfo["varietyid"],max_phone_num)
        phones = set()
        for i in userphones:
            phones.add(str(i["phone"]))
        for j in yt:
            phones.add(str(j["mobile"]))
        phones = list(set(phones))
        if len(phones)!=0:
            taskinfo = {"taskid": taskid, "sendlist":",".join(phones)}
            collection = mongodb.celery_task_info
            collection.insert(taskinfo)
        sendkafka.apply_async(args=[taskid])

        task = {"purchaseinfoid": purchaseinfoid, "tasktype": tasktype, "channel": 2, "order": order,"status":0}
        taskid = mongodb.celery_task.insert(task)
        userwxs = sqldb.query(
                "select openid from users where find_in_set(%s,varietyids) and openid!=''"+wxcondition+" order by pushscore limit 0,%s",
                purchaseinfo["varietyid"], max_wx_num)
        openids = set()
        for i in userwxs:
            openids.add(str(i["openid"]))
        openids =list(openids)
        if len(openids)!=0:
            taskinfo = {"taskid": taskid, "sendlist": ",".join(openids)}
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
    print "analysis_record"
    pass


@celerysever.task
def analysis_notify():#定时检测报价回复情况，生成提醒
    print "analysis_notify"
    pass


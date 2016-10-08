#coding:utf8
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
SPARK_HOME = os.environ['SPARK_HOME']
sys.path.insert(0, os.path.join(SPARK_HOME, "python", "lib"))
sys.path.insert(0, os.path.join(SPARK_HOME, "python"))

import json
from globalconfig import *
from mongodb import PymongoDateBase
from database import database
import time
from bson import ObjectId
from utils import *
import thread

def sendPush(rdd):
    if rdd.isEmpty() is False:
        resultList = rdd.collect()
        for item in resultList:
            taskid=item["taskid"]
            mongodb = PymongoDateBase.instance().get_db()
            sqldb = database.instance().get_session()
            taskid=ObjectId(taskid)
            task= mongodb.celery_task.find_one({"_id":taskid})
            if task:
                mongodb.celery_task.update({"_id":taskid}, {'$set':{'status':1}})
                purchaseinfoid=task["purchaseinfoid"]
                count=task["order"]
                channel=task["channel"]
                tasktype=task["tasktype"]
                taskinfo=mongodb.celery_task_info.find_one({"taskid":taskid})
                if taskinfo:
                    sendlist=taskinfo["sendlist"].split(",")
                    if tasktype==1:
                        purchaseinfo = sqldb.get("select pi.id purchaseinfoid,pi.varietyid,pi.name variety,pi.specification,pi.quantity,pi.unit,pi.quality,pi.origin,pi.pushcount,p.userid,p.createtime from purchase_info pi left join purchase p on pi.purchaseid = p.id where pi.id = %s", purchaseinfoid)
                        u = sqldb.get("select name,nickname from users where id = %s", purchaseinfo["userid"])
                        purchaseinfo["name"] = u["name"]
                        purchaseinfo["nickname"] = u["nickname"]
                        push_user_infos = []
                        uuidmap={}
                        sendstatus = 0  # 0,未发送，1:发送成功,2:失败
                        colleciton = mongodb.transform_rate
                        createtime = int(time.time())
                        if channel==1 and  purchaseinfo["openid"]=="" and purchaseinfo["maxpush"]>3:
                            return
                        push_id=colleciton.insert({"purchaseinfoid":purchaseinfoid ,"varietyname":purchaseinfo["variety"],"order":count,"quote":"","type":channel,"createtime":createtime})
                        for send in sendlist:
                            uuid = md5(str(time.time())+ str(send))[8:-8]
                            sendid = send
                            createtime = int(time.time())
                            push_user = {"pushid":push_id ,"uuid":uuid,"createtime":createtime,"click":0,"sendid":sendid,"sendstatus":sendstatus,"type":channel}
                            push_user_infos.append(push_user)
                            uuidmap[sendid]=uuid

                        colleciton = mongodb.push_record
                        colleciton.insert_many(push_user_infos)
                        if channel==1:
                            print sendlist, purchaseinfo, uuidmap
                            #pushPurchase(sendlist, purchaseinfo, uuidmap)
                            attentions=[]#关注用户
                            notattentions=[]#非关注用户
                            for phone in sendlist:
                                userinfo = None
                                userinfo=sqldb.get("select id,maxpush,openid from users where phone=%s",phone)
                                if userinfo and userinfo["openid"]!="":
                                    attentions.append(phone)
                                else:
                                    notattentions.append(phone)
                                    sqldb.execute("update users set maxpush=maxpush+1 where phone=%s",
                                                  phone)
                            if len(notattentions)!=0:
                                thread.start_new_thread(pushPurchase, (sendlist, purchaseinfo, uuidmap,2))
                            if len(attentions) != 0:
                                thread.start_new_thread(pushPurchase, (sendlist, purchaseinfo, uuidmap))
                        else:
                            print sendlist, purchaseinfo,uuidmap
                            #pushPurchaseWx(sendlist, purchaseinfo,uuidmap)
                            thread.start_new_thread(pushPurchaseWx, (sendlist, purchaseinfo, uuidmap))
                    elif tasktype==2:
                        sendid=taskinfo["sendlist"]
                        print purchaseinfoid
                        ret = sqldb.query("select id from quote where purchaseinfoid =%s and state=0", purchaseinfoid)#未回复的报价个数
                        num=len(ret)
                        if num!=0:
                            ret= sqldb.query("select id from quote where purchaseinfoid =%s and state=0 order by price", purchaseinfoid)
                            qid=ret[0]["id"]
                            purchaseinfo = sqldb.get("select pi.name,pi.purchaseid,pi.unit,q.price from quote q left join  purchase_info pi on q.purchaseinfoid=pi.id where q.id=%s",qid)
                            if channel==1:
                                if sendid!="":
                                    uuid = md5(str(time.time()) + str(sendid))[8:-8]
                                    createtime = int(time.time())
                                    push_user = {"pushid": "", "uuid": uuid, "createtime": createtime, "click": 0,
                                                 "sendid": sendid, "sendstatus": 0, "type": channel}
                                    colleciton = mongodb.push_record
                                    record_id=colleciton.insert(push_user)

                                    colleciton = mongodb.notify_record
                                    notify_user = {"createtime": int(time.time()), "sendid": sendid, "type": channel,"purchaseinfoid":purchaseinfoid,"recordid":record_id}
                                    colleciton.insert(notify_user)
                                    #print sendid, str(num),purchaseinfo["name"].encode("utf8"),purchaseinfo["price"].encode("utf8"),purchaseinfo["unit"].encode("utf8"),str(purchaseinfo["purchaseid"])
                                    #reply_quote_notify(sendid, str(num), purchaseinfo["name"],purchaseinfo["price"], purchaseinfo["unit"], str(purchaseinfoid))
                                    thread.start_new_thread(reply_quote_notify,(sendid, str(num), purchaseinfo["name"],purchaseinfo["price"], purchaseinfo["unit"], str(purchaseinfoid),uuid))

                            elif channel==2:
                                print sendid
                                if sendid!="":
                                    user=sqldb.query("select id from users where openid=%s", sendid)
                                    if user:
                                        sendtype=1
                                    else:
                                        sendtype=2
                                    uuid = md5(str(time.time()) + str(sendid))[8:-8]
                                    createtime = int(time.time())
                                    push_user = {"pushid": "", "uuid": uuid, "createtime": createtime, "click": 0,
                                                 "sendid": sendid, "sendstatus": 0, "type": channel}
                                    colleciton = mongodb.push_record
                                    record_id = colleciton.insert(push_user)

                                    colleciton = mongodb.notify_record
                                    notify_user = {"createtime": int(time.time()), "sendid": sendid, "type": channel,"purchaseinfoid":purchaseinfoid,"recordid":record_id}
                                    colleciton.insert(notify_user)
                                    #print sendid, str(num),purchaseinfo["name"].encode("utf8"),purchaseinfo["price"].encode("utf8"),purchaseinfo["unit"].encode("utf8"),str(purchaseinfo["purchaseid"]),sendtype
                                    #reply_wx_notify(sendid, str(num), purchaseinfo["name"],purchaseinfo["price"], purchaseinfo["unit"], str(purchaseinfoid),str(purchaseinfo["purchaseid"]))
                                    thread.start_new_thread(reply_wx_notify, (sendid, str(num), purchaseinfo["name"],purchaseinfo["price"], purchaseinfo["unit"], str(purchaseinfoid),str(purchaseinfo["purchaseid"]),uuid,sendtype))
                                    pass




def handlestream(kvs):
    parsed = kvs.map(lambda (k, v): json.loads(v))#获取消息的json格式
    #处理发送任务
    send=parsed.filter(lambda x: True if x["messagetype"] == 2  else False)
    send.foreachRDD(sendPush)





if __name__ == "__main__":
    sc = SparkContext(appName="sendKafka")
    ssc = StreamingContext(sc, 1)
    kvs = KafkaUtils.createStream(ssc, zk_server, "send-group", {send_task_topic: 1})
    handlestream(kvs)
    ssc.start()
    ssc.awaitTermination()

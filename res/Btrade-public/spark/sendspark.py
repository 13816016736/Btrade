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
            taskid=ObjectId(taskid)
            task= mongodb.celery_task.find_one({"_id":taskid})
            if task:
                mongodb.celery_task.update({"_id":taskid}, {'$set':{'status':1}})
                purchaseinfoid=task["purchaseinfoid"]
                count=task["order"]
                type=task["channel"]
                taskinfo=mongodb.celery_task_info.find_one({"taskid":taskid})
                if taskinfo:
                    sendlist=taskinfo["sendlist"].split(",")
                    sqldb = database.instance().get_session()
                    purchaseinfo = sqldb.get("select pi.id purchaseinfoid,pi.varietyid,pi.name variety,pi.specification,pi.quantity,pi.unit,pi.quality,pi.origin,pi.pushcount,p.userid,p.createtime from purchase_info pi left join purchase p on pi.purchaseid = p.id where pi.id = %s", purchaseinfoid)
                    u = sqldb.get("select name,nickname from users where id = %s", purchaseinfo["userid"])
                    purchaseinfo["name"] = u["name"]
                    purchaseinfo["nickname"] = u["nickname"]
                    push_user_infos = []
                    uuidmap={}
                    sendstatus = 0  # 0,未发送，1:发送成功,2:失败
                    colleciton = mongodb.transform_rate
                    createtime = int(time.time())
                    push_id=colleciton.insert({"purchaseinfoid":purchaseinfoid ,"order":count,"quote":"","type":type,"createtime":createtime})

                    for send in sendlist:
                        uuid = md5(str(time.time())+ str(send))[8:-8]
                        sendid = send
                        createtime = int(time.time())
                        push_user = {"pushid":push_id ,"uuid":uuid,"createtime":createtime,"click":0,"sendid":sendid,"sendstatus":sendstatus,"type":type}
                        push_user_infos.append(push_user)
                        uuidmap[sendid]=uuid

                    colleciton = mongodb.push_record
                    colleciton.insert_many(push_user_infos)
                    if type==1:
                        print sendlist, purchaseinfo, uuidmap
                        #pushPurchase(sendlist, purchaseinfo, uuidmap)
                        #thread.start_new_thread(pushPurchase, (sendlist, purchaseinfo, uuidmap))
                    else:
                        print sendlist, purchaseinfo,uuidmap
                        #pushPurchaseWx(sendlist, purchaseinfo,uuidmap)
                        #thread.start_new_thread(pushPurchaseWx, (sendlist, purchaseinfo, uuidmap))



def handlestream(kvs):
    parsed = kvs.map(lambda (k, v): json.loads(v))#获取消息的json格式
    #处理发送任务
    send=parsed.filter(lambda x: True if x["messagetype"] == 2 else False)
    send.foreachRDD(sendPush)




if __name__ == "__main__":
    sc = SparkContext(appName="sendKafka")
    ssc = StreamingContext(sc, 1)
    kvs = KafkaUtils.createStream(ssc, zk_server, "send-group", {send_task_topic: 1})
    handlestream(kvs)
    ssc.start()
    ssc.awaitTermination()

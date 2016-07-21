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

def sendTask(rdd):
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
                    sendlist=taskinfo["sendlist"]
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
                        push_user = {"pushid":push_id ,"uuid":uuid,"createtime":createtime,"click":0,"sendid":sendid,"sendstatus":sendstatus,"type":1}
                        push_user_infos.append(push_user)
                        uuidmap[sendid]=uuid

                    colleciton = mongodb.push_record
                    colleciton.insert_many(push_user_infos)
                    if type==1:
                        pushPurchase(sendlist, purchaseinfo, uuidmap)
                    else:
                        pushPurchaseWx(sendlist, purchaseinfo,uuidmap)


def handlestream(kvs):
    parsed = kvs.map(lambda (k, v): json.loads(v))#获取消息的json格式
    #处理发送任务
    send=parsed.filter(lambda x: True if x["messagetype"] == 2 else False)
    send.foreachRDD(sendTask)

def pushPurchase(phones, purchase,uuidmap):
    templateId = 870
    for (k,v) in purchase.items():
        purchase[k] = purchase[k].encode('utf-8') if isinstance(purchase[k], unicode) else purchase[k]
    #vars = '{"%purchaseinfoid%":"'+str(purchase["purchaseinfoid"])+'","%variety%":"'+purchase["variety"]+'","%name%":"'+purchase["name"]+'","%specification%":"'+purchase["specification"]+'","%quantity%":"'+purchase["quantity"]+'","%unit%":"'+purchase["unit"]+'"}'
    tos = []
    num = 0
    phonelist=[]
    for index, phone in enumerate(phones):
        num = num + 1
        phone = phone.encode('utf-8') if isinstance(phone, unicode) else phone
        uuid=uuidmap[phone]
        vars = '{"%purchaseinfoid%":"' + str(purchase["purchaseinfoid"]) +'?uuid='+ uuid +'","%variety%":"' + purchase[
            "variety"] + '","%name%":"' + purchase["name"] + '","%specification%":"' + purchase[
                   "specification"] + '","%quantity%":"' + purchase["quantity"] + '","%unit%":"' + purchase[
                   "unit"] + '"}'
        tos.append('{"phone": "'+phone+'", "vars": '+vars+'}')
        phonelist.append(phone)
        if num > 199:
            tos = "[" + ",".join(tos) + "]"
            #sendx(templateId, tos)
            print templateId, tos
            tos = []
            num = 0
            phonelist=[]
        elif index == (len(phones)-1):
            tos = "[" + ",".join(tos) + "]"
            #sendx(templateId, tos)
            print templateId, tos
def pushPurchaseWx(openids, purchase,uuidmap):
    templateId = 'OxXsRhlyc17kt6ubwV7F0fD8ffRl12rGGS3mnpvpoU4'
    link = 'http://m.yaocai.pro/purchase/purchaseinfo/%s' % purchase["purchaseinfoid"]
    qtime = int(purchase["createtime"])
    purchase["name"] = purchase["name"].encode('utf-8') if isinstance(purchase["name"], unicode) else purchase["name"]
    purchase["variety"] = purchase["variety"].encode('utf-8') if isinstance(purchase["variety"], unicode) else purchase["variety"]
    purchase["specification"] = purchase["specification"].encode('utf-8') if isinstance(purchase["specification"], unicode) else purchase["specification"]
    purchase["origin"] = purchase["origin"].encode('utf-8') if isinstance(purchase["origin"], unicode) else purchase["origin"]
    purchase["quality"] = purchase["quality"].encode('utf-8') if isinstance(purchase["quality"], unicode) else purchase["quality"]
    purchase["quantity"] = purchase["quantity"].encode('utf-8') if isinstance(purchase["quantity"], unicode) else purchase["quantity"]
    purchase["unit"] = purchase["unit"].encode('utf-8') if isinstance(purchase["unit"], unicode) else purchase["unit"]
    for openid in openids:
        openid = openid.encode('utf-8') if isinstance(openid, unicode) else openid
        data = {
            "first": {
               "value":"%s 邀请您报价" % purchase["name"],
               "color":"#173177"
            },
            "keyword1": {
               "value":"%s（%s），产地：%s，%s" % (purchase["variety"],purchase["specification"],purchase["origin"],purchase["quality"]),
               "color":"#173177"
            },
            "keyword2": {
               "value":"%s%s" % (purchase["quantity"],purchase["unit"]),
               "color":"#173177"
            },
            "keyword3":{
               "value":purchase["nickname"],
               "color":"#173177"
            },
            "keyword4": {
                "value": time.strftime("%Y年%m月%d日 %H:%M", time.localtime(qtime)),
                "color": "#173177"
            },
            "remark":{
               "value":"点击“详情”，立即报价",
               "color":"#173177"
            }
        }
        uuid = uuidmap[openid]
        link=link+"?uuid="+uuid
        print templateId, openid, link, data
        #reuslt=sendwx(templateId, openid, link, data)
        #if reuslt:
        #    message = json.loads(reuslt.encode("utf-8"))
        #    db = PymongoDateBase.instance().get_db()
        #    colleciton = db.push_record
        #    if message["errcode"]==0:
        #        colleciton.update({'uuid': uuid}, {'$set': {'sendstatus': 1}})
        #    else:
        #        colleciton.update({'uuid': uuid}, {'$set': {'sendstatus': 2}})
        time.sleep(3)

def md5(str):
    import hashlib
    import types
    if type(str) is types.StringType:
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    else:
        return ''


if __name__ == "__main__":
    sc = SparkContext(appName="sendKafka")
    ssc = StreamingContext(sc, 1)
    kvs = KafkaUtils.createStream(ssc, zk_server, "send-group", {send_task_topic: 1})
    handlestream(kvs)
    ssc.start()
    ssc.awaitTermination()

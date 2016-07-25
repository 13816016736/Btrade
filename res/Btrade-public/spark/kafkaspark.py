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

def parse(json):
    if  json["messagetype"]==1:
        if json["userid"]!=-1:
            return json
    else:
        return None

def writeDB(rdd):
    if rdd.isEmpty() is False:
        resultList=rdd.collect()
        for item in resultList:
            mongodb = PymongoDateBase.instance().get_db()
            colleciton = mongodb.push_record
            uuid=item["uuid"]
            quoteid=item["quoteid"]
            sqldb = database.instance().get_session()
            ret=sqldb.get("select purchaseinfoid from quote where id=%s",quoteid)
            if ret:
                qinfoid=ret["purchaseinfoid"]
                record = colleciton.find_one({"uuid": uuid})
                if record:
                    pushid=record["pushid"]
                    transform=mongodb.transform_rate.find_one({"_id":pushid})
                    if transform:
                        purchaseinfoid=transform["purchaseinfoid"]
                        quote=[]
                        if transform["quote"]!="":
                            quote=transform["quote"].split(",")
                        if str(qinfoid)==str(purchaseinfoid):#如果是推送的批次采购则进入统计
                            if str(quoteid) not in quote:
                                quote.append(str(quoteid))
                            mongodb.transform_rate.update({"_id":pushid}, {'$set':{'quote':','.join(quote)}})





def writeAll(rdd):#纯记录用户数据
    if rdd.isEmpty() is False:
        resultList=rdd.collect()
        for item in resultList:
                db = PymongoDateBase.instance().get_db()
                colleciton = db.user_view
                colleciton.insert(item)

def filterMethod(item):
    if item is not None:
        if item["url"].find("/quotesuccess")== 0 and item["method"].upper() == "POST" and item["quoteid"]!=-1:#报价成功
            return True
    return False

def filterClick(item):
    uuid=item["uuid"]
    if item["messagetype"] == 1 and item["url"].find("/purchase/purchaseinfo/") == 0 and item["url"].find("?uuid="+uuid)!=-1 :
        return True
    else:
        return False

def storeClick(rdd):
    if rdd.isEmpty() is False:
        resultList = rdd.collect()
        for item in resultList:
            mongodb = PymongoDateBase.instance().get_db()
            uuid = item["uuid"]
            colleciton = mongodb.push_record
            record=colleciton.find_one({"uuid":uuid})
            if record:
                click=record["click"]
                type=record["type"]
                sendid=record["sendid"]
                if click==0:
                    sqldb = database.instance().get_session()
                    if type==1:#短信推送
                        supplier=sqldb.query("select id,pushstatus from supplier where  mobile=%s ",sendid)
                        print supplier
                        if supplier and supplier[0]["pushstatus"]!=2:
                            sqldb.execute("update supplier set pushscore=pushscore+1 where mobile=%s",sendid)
                        else:
                            sqldb.execute("update  users set pushscore=pushscore+1 where phone=%s", sendid)
                    elif type==2:#微信推送
                        sqldb.execute("update  users set pushscore=pushscore+1 where openid=%s", sendid)
                click=click+1
                colleciton.update({'uuid':uuid}, {'$set':{'click':click}})






def handlestream(kvs):
    parsed = kvs.map(lambda (k, v): json.loads(v))#获取消息的json格式
    parsed.filter(lambda x:True if x["messagetype"]==1 else False).foreachRDD(writeAll)#将用户路径消息写入mongodb

    click_count=parsed.filter(filterClick)
    click_count.foreachRDD(storeClick)#统计点击以及点击加分

    summed = parsed.map(parse).filter(filterMethod)#获取报价成功的用户
    summed.foreachRDD(writeDB)#写入mongodb




    #summed.pprint()

if __name__ == "__main__":
    sc = SparkContext(appName="PythonStreamingKafka")
    ssc = StreamingContext(sc, 1)
    kvs = KafkaUtils.createStream(ssc, zk_server, "my-group", {analysis_send_topic: 1})
    #kvs = KafkaUtils.createDirectStream(ssc, [analysis_send_topic], {"metadata.broker.list": kafka_server})
    handlestream(kvs)
    ssc.start()
    ssc.awaitTermination()

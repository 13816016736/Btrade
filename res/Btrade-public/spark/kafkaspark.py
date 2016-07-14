#coding:utf8
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))

import json
from globalconfig import *
from mongodb import PymongoDateBase

def parse(json):
    if json["userid"]!=-1:
        return json
    else:
        return None
def writeDB(rdd):
    if rdd.isEmpty() is False:
        resultList=rdd.collect()
        for item in resultList:
            db = PymongoDateBase.instance().get_db()
            colleciton = db.push_record
            uuid=item["uuid"]
            colleciton.update({'uuid':uuid}, {'$set':{'quote':1}})
def filterMethod(item):
    if item is not None:
        if item["url"].find("/quotesuccess")== 0 and item["method"].upper() == "POST" :#报价成功
            return True

    return False

def handlestream(kvs):
    parsed = kvs.map(lambda (k, v): json.loads(v))#获取消息的json格式
    summed = parsed.map(parse).filter(filterMethod)#获取报价成功的用户
    summed.foreachRDD(writeDB)#写入mongodb
    #summed.pprint()

if __name__ == "__main__":
    sc = SparkContext(appName="PythonStreamingKafka")
    ssc = StreamingContext(sc, 1)
    kvs = KafkaUtils.createStream(ssc, zk_server, "test-group", {analysis_send_topic: 1})
    #kvs = KafkaUtils.createDirectStream(ssc, [analysis_send_topic], {"metadata.broker.list": kafka_server})
    handlestream(kvs)
    ssc.start()
    ssc.awaitTermination()

from pyspark.sql import SQLContext
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))

import json
from globalconfig import *


if __name__ == "__main__":
    #APP_NAME = "Flight Delay Analysis"
    # set up our contexts
    sc = SparkContext(appName="PythonStreamingKafkaWordCount")
    ssc = StreamingContext(sc, 1)

    #zkQuorum, topic = sys.argv[1:]
    kvs = KafkaUtils.createStream(ssc, zk_server, "", {"analysis_send_topic": 1})
    parsed = kvs.map(lambda (k, v): json.loads(v))
    print parsed

    ssc.start()
    ssc.awaitTermination()
    #parsed = kafka_stream.map(lambda (k, v): json.loads(v))
    #summed = parsed.map(lambda event: (event['site_id'], 1)). \
    #    reduceByKey(lambda x, y: x + y). \
    #    map(lambda x: {"site_id": x[0], "ts": str(uuid1()), "pageviews": x[1]})

    #stream.start()
    #stream.awaitTermination()
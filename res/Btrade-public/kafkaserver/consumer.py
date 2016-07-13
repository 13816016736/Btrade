from kafka import KafkaConsumer
import json
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
from globalconfig import *
# kafka consumer

class KafkaConsumerServer(object):
    def __init__(self,topic,server):
        if type(server)!=list:
            server=[server]
        self._consumer= KafkaConsumer(topic,
                         bootstrap_servers=server,
                         value_deserializer=lambda m: json.loads(m.decode('utf8')))
    def getConsumer(self):
        return self._consumer




if __name__ == "__main__":
    kafkaserver = KafkaConsumerServer(analysis_send_topic,kafka_server)
    for message in kafkaserver.getConsumer():
        print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
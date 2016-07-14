from kafka import KafkaProducer
import json
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
from globalconfig import *


#kafka Produce
class KafkaProduceServer(object):
    def __init__(self, topic, server):
        if type(server) != list:
            server = [server]
        self._topic=topic
        self._producer = KafkaProducer(bootstrap_servers=server,value_serializer=lambda m: json.dumps(m).encode('ascii'))
    def getProducer(self):
        return self._producer
    def sendMsg(self,msg):
        self._producer.send(self._topic,msg)
        self._producer.flush()
    def sendJson(self,key,json):
        self._producer.send(self._topic,key=key,value=json)
        self._producer.flush()
    def close(self):
        self._producer.close()



if __name__ == "__main__":
    producer_server = KafkaProduceServer(analysis_send_topic,kafka_server)
    producer_server.sendJson("data",{'uuid': '2222222', "url": "/login", "monitor_type": "15"})
    #producer_server.sendMsg('raw_bytes')
    '''
    # Asynchronous by default
    future = producer.send('my-topic', b'raw_bytes')

    # Block for 'synchronous' sends
    try:
        record_metadata = future.get(timeout=10)
    except KafkaError,Ex:
        # Decide what to do if produce request failed...
        str(Ex)
        pass

    # Successful result returns assigned partition and offset
    print (record_metadata.topic)
    print (record_metadata.partition)
    print (record_metadata.offset)
    '''

    # produce keyed messages to enable hashed partitioning
    #producer.send('test', key=b'foo', value=b'bar')
    #producer.flush()

    #producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('ascii'))
    #producer.send('test', key="data",value={'uuid': '2222222',"url":"/login","monitor_type":"3"})

    # configure multiple retries
    #producer = KafkaProducer(retries=5)

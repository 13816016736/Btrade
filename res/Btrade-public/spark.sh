sudo nohup /opt/spark/bin/spark-submit --jars /opt/spark/lib/spark-streaming-kafka-assembly_2.10-1.6.2.jar spark/kafkaspark.py &
sudo nohup /opt/spark/bin/spark-submit --jars /opt/spark/lib/spark-streaming-kafka-assembly_2.10-1.6.2.jar spark/sendspark.py &

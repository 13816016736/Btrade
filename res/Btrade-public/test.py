#coding:utf8
from pushengine.tasks import analysis_notify,analysis_record,sendkafka
from datetime import timedelta,datetime
import time
r = analysis_record.apply_async()

#print "Result:",r.get()
#yesterday=datetime.now()-timedelta(days=1)
#print time.time()
#timeStamp=time.mktime(yesterday.timetuple())
#timeArray = time.localtime(timeStamp)
#otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
#print otherStyleTime

#sendkafka.apply_async(args=["5791d391fd7589256877f1ae"])
#from utils import reply_wx_notify
#openid="oTEeNweXKZh8FXoP3Fwu_y3AGPkk"
#num='3'
#name='五味子'
#price="10"
#unit="斤"
#pid="371"
#purchaseid="146112075263"
#reply_wx_notify(openid,num, name, price, unit,pid,purchaseid)



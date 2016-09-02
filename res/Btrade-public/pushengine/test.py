#coding:utf8
#from datetime import timedelta,datetime
import time
import sys,os
sys.path.append(os.path.join(sys.path[0],".."))
#r = analysis_record.apply_async()

#print "Result:",r.get()
#yesterday=datetime.now()-timedelta(days=1)
#print time.time()
#timeStamp=time.mktime(yesterday.timetuple())
#timeArray = time.localtime(1469784474)
#otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
#print otherStyleTime

#sendkafka.apply_async(args=["5791d391fd7589256877f1ae"])
#from utils import reply_wx_notify,reply_quote_notify
#openid="oTEeNweXKZh8FXoP3Fwu_y3AGPkk"
#phone="13638654365"
#num='3'
#name='五味子'
#price="10"
#unit="斤"
#pid="371"
#purchaseid="146112075263"
#uuid="112223344"
#reply_wx_notify(openid,num, name, price, unit,pid,purchaseid,uuid)
#reply_quote_notify(phone, num, name, price, unit,pid,uuid)

#print '\xe4\xba\xb3\xe5\xb7\x9e'
#regSuccessWx("oTEeNweXKZh8FXoP3Fwu_y3AGPkk", "肖先生", "ycg")
from pushengine.tasks import task_generate
task = {"purchaseinfoid": str("525"), "tasktype": 2, "channel": 2}
print task
task_generate.apply_async(args=[task])
#coding:utf8
#from datetime import timedelta,datetime
#import time
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
#from pushengine.tasks import task_generate
##print task
#task_generate.apply_async(args=[task])
from mongodb import PymongoDateBase
from database import database
import pymongo
from datetime import timedelta,datetime
import time
'''
print "start analysis_record start"
def update(phone,list):
    for item in list:
        if item["phone"]==phone:
            item["notclick"]+=1
    return
mongodb = PymongoDateBase.instance().get_db()
sqldb = database.instance().get_session()
# items =mongodb.transform_rate.find()#检测发送超过一天的统计记录 条件通过createtime
format = "%Y-%m-%d"
todaystr = datetime.now().strftime("%Y-%m-%d")
print todaystr
today = datetime.strptime(todaystr, format)
yesterday = today - timedelta(days=7)

todayStamp = time.mktime(today.timetuple())
yesterdayStamp = time.mktime(yesterday.timetuple())
print todayStamp
print yesterdayStamp
yesterdayStamp=0

ret = mongodb.push_record.find({"createtime": {"$gt": int(yesterdayStamp), "$lt": int(todayStamp)},"type":1})
alluser=set()
for item in ret:
    alluser.add(item["sendid"])
alluser=list(alluser)
totalcount=len(alluser)
notclick=[]
for item in alluser:
    user={"phone":item,"notclick":0}
    notclick.append(user)
ret = mongodb.push_record.find({"createtime": {"$gt": int(yesterdayStamp), "$lt": int(todayStamp)},"type":1})
for item in ret:
    if item["click"]==0:
        update(item["sendid"],notclick)

notnum=0
for item in notclick:
    if item["notclick"]>3:
        notnum+=1
print totalcount
print notnum
'''
mongodb = PymongoDateBase.instance().get_db()
sqldb = database.instance().get_session()
# items =mongodb.transform_rate.find()#检测发送超过一天的统计记录 条件通过createtime
format = "%Y-%m-%d"
todaystr = datetime.now().strftime("%Y-%m-%d")
print todaystr
todaystr="2016-09-28"
today = datetime.strptime(todaystr, format)
yesterday = today - timedelta(days=4)

todayStamp = time.mktime(today.timetuple())
yesterdayStamp = time.mktime(yesterday.timetuple())
print todayStamp
print yesterdayStamp

ret = mongodb.push_record.find({"createtime": {"$gt": int(yesterdayStamp), "$lt": int(todayStamp)}, "type": 1})
for item in ret:
    if item["click"] == 0:
        sqldb.execute("update supplier set maxpush=maxpush+1 where mobile=%s",
                      item["sendid"])

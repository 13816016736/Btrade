#coding:utf8
import tornado.web
from base import BaseHandler
from mongodb import PymongoDateBase
from datetime import datetime
import time

class PushRecordHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        starttime= self.get_argument("starttime", "")
        endtime=self.get_argument("endtime", "")
        push_type=self.get_argument("type", 1)
        mongodb = PymongoDateBase.instance().get_db()
        if int(push_type)==1:
            start_time=0
            end_time=0
            if starttime!="" and endtime!="":
                start_time = int(time.mktime(datetime.strptime(str(starttime), "%Y-%m-%d %H:%M").timetuple()))
                end_time= int(time.mktime(datetime.strptime(str(endtime), "%Y-%m-%d %H:%M").timetuple()))
            if starttime!=0 and end_time!=0:
                items=mongodb.transform_rate.find({"createtime":{"$gt":int(start_time),"$lt":int(end_time)}})
            else:
                items = mongodb.transform_rate.find()
            for item in items:
                print item
        elif int(push_type)==2:
            pass
        self.render("push_record.html", starttime=starttime,
                    endtime=endtime,type=push_type)
#coding:utf8
import tornado.web
from base import BaseHandler
from mongodb import PymongoDateBase
from datetime import datetime
import time
from config import *

class PushRecordHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        starttime= self.get_argument("starttime", "")
        endtime=self.get_argument("endtime", "")
        channel=self.get_argument("channel", -1)
        pid = self.get_argument("pid", "")
        push_type = self.get_argument("type", 1)
        mongodb = PymongoDateBase.instance().get_db()
        records=[]
        start_time = 0
        end_time = 0
        page = self.get_argument("page", 0)
        page = (int(page) - 1) if page > 0 else 0
        limit_num=config.conf['POST_NUM']
        skip_num=page * config.conf['POST_NUM']
        num=0
        if starttime != "" and endtime != "":
            start_time = int(time.mktime(datetime.strptime(str(starttime), "%Y-%m-%d %H:%M").timetuple()))
            end_time = int(time.mktime(datetime.strptime(str(endtime), "%Y-%m-%d %H:%M").timetuple()))
        condition={}
        if start_time != 0 and end_time != 0:
            condition["createtime"]={"$gt":int(start_time),"$lt":int(end_time)}
        if int(channel)!=-1:
            condition["type"]=int(channel)
        if pid!="":
            condition["purchaseinfoid"]=pid
        if int(push_type)==1:
            items = mongodb.transform_rate.find(condition).skip(skip_num).limit(limit_num)
            num =mongodb.transform_rate.find(condition).count()
            for item in items:
                purchaseinfoid=item["purchaseinfoid"]
                ret=self.db.get("select varietyid,name from purchase_info where id=%s",purchaseinfoid)
                if ret:
                    item["varietyname"]=ret["name"]
                else:
                    item["varietyname"] =u"不存在"
                if item["quote"]=="":
                    item["quotetime"]=0
                else:
                    item["quotetime"]=len(item["quote"].split(","))
                item["type"]=monitor_type[str(item["type"])]
                push_count = mongodb.push_record.find({"pushid": item["_id"]}).count()
                item["pushcount"]=push_count
                if push_count != 0:
                    item["clickcount"] = mongodb.push_record.find({"pushid": item["_id"], "click": {'$gt': 0}}).count()
                else:
                    item["clickcount"] =0
                timeArray = time.localtime(item["createtime"])
                item["time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                record={"purchaseinfoid":purchaseinfoid,"order":item["order"],"varietyname":item["varietyname"],
                        "quotetime": item["quotetime"],"type":item["type"],"pushcount":item["pushcount"],"clickcount":item["clickcount"],
                        "time":item["time"],"id":item["_id"]
                        }
                records.append(record)
        elif int(push_type)==2:
            items = mongodb.notify_record.find(condition).skip(skip_num).limit(limit_num)
            num=mongodb.notify_record.find(condition).count()
            for item in items:
                purchaseinfoid = item["purchaseinfoid"]
                ret=self.db.get("select varietyid,name from purchase_info where id=%s",purchaseinfoid)
                if ret:
                    item["varietyname"]=ret["name"]
                else:
                    item["varietyname"] =u"不存在"
                push_count = mongodb.push_record.find({"pushid": item["_id"]}).count()
                item["pushcount"] = push_count
                item["type"] = monitor_type[str(item["type"])]
                timeArray = time.localtime(item["createtime"])
                item["time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                record = {"purchaseinfoid": purchaseinfoid, "varietyname": item["varietyname"],
                          "type": item["type"], "pushcount": item["pushcount"],"time": item["time"], "id": item["_id"]
                          }
                records.append(record)
        query_str={}
        query_str["type"]=push_type
        if starttime!="":
            query_str["starttime"]=starttime
        if endtime!="":
            query_str["endtime"] = endtime
        if int(channel)!=-1:
            query_str["channel"] = channel
        nav = {
            'model': 'stat/pushrecord',
            'cur': page + 1,
            'num': num,
            'query': "%s" % urlencode(query_str),
        }
        self.render("push_record.html", starttime=starttime,channel=channel,pid=pid,
                    endtime=endtime,type=push_type,records=records,nav=nav)
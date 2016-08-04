#coding:utf8
import tornado.web
from base import BaseHandler
from mongodb import PymongoDateBase
from datetime import datetime
import time
from config import *
from bson import ObjectId
from urllib import urlencode

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
            items = mongodb.transform_rate.find(condition).sort([("createtime",-1)]).skip(skip_num).limit(limit_num)
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
            items = mongodb.notify_record.find(condition).sort([("createtime",-1)]).skip(skip_num).limit(limit_num)
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

class RecordDetailHandler(BaseHandler):
       @tornado.web.authenticated
       def get(self):
           pushid=self.get_argument("id", "")
           mongodb = PymongoDateBase.instance().get_db()
           record={}
           detail=[]
           page = self.get_argument("page", 0)
           page = (int(page) - 1) if page > 0 else 0
           limit_num = config.conf['POST_NUM']
           skip_num = page * config.conf['POST_NUM']
           num = 0
           if pushid!="":
               item=mongodb.transform_rate.find_one(ObjectId(pushid))
               purchaseinfoid = item["purchaseinfoid"]
               ret = self.db.get("select varietyid,name from purchase_info where id=%s", purchaseinfoid)
               if ret:
                   item["varietyname"] = ret["name"]
               else:
                   item["varietyname"] = u"不存在"
               if item["quote"] == "":
                   item["quotetime"] = 0
               else:
                   item["quotetime"] = len(item["quote"].split(","))
               item["type"] = monitor_type[str(item["type"])]
               push_count = mongodb.push_record.find({"pushid": item["_id"]}).count()
               item["pushcount"] = push_count
               if push_count != 0:
                   item["clickcount"] = mongodb.push_record.find({"pushid": item["_id"], "click": {'$gt': 0}}).count()
               else:
                   item["clickcount"] = 0
               timeArray = time.localtime(item["createtime"])
               item["time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
               record = {"purchaseinfoid": purchaseinfoid, "order": item["order"], "varietyname": item["varietyname"],
                         "quotetime": item["quotetime"], "type": item["type"], "pushcount": item["pushcount"],
                         "clickcount": item["clickcount"],
                         "time": item["time"], "id": item["_id"]
                         }

               pushrecords=mongodb.push_record.find({"pushid":item["_id"]}).skip(skip_num).limit(limit_num)
               num=mongodb.push_record.find({"pushid":item["_id"]}).count()
               for pushrecord in pushrecords:
                   uuid=pushrecord["uuid"]
                   sendstatus=pushrecord["sendstatus"]
                   monitortype=pushrecord["type"]
                   sendid=pushrecord["sendid"]
                   item={}
                   click=0
                   register=0#0未注册，1注册，2已经注册过
                   quote=0
                   accept=0
                   reject=0
                   timeArray = time.localtime(pushrecord["createtime"])
                   item["createtime"] = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                   if pushrecord["click"]!=0:
                       click=1
                   if monitortype==1:
                        user=self.db.get("select id from users where phone=%s",sendid)
                        if user:
                            registerurl=mongodb.user_view.find({"uuid":uuid,"url":{"$regex":"^/regsuccess"}}).count()
                            if registerurl!=0:
                                register= 1
                            else:
                                register = 2
                   else:
                        register = 2
                   quoteurl=mongodb.user_view.find_one({"uuid":uuid,"url":{"$regex":"^/quotesuccess"}})
                   if quoteurl:
                        quote=1
                        qid=quoteurl["quoteid"]
                        quoteinfo=self.db.get("select id state from quote where id=%s",qid)
                        if quoteinfo:
                            if quoteinfo["state"]==1:
                                accept=1
                            elif quoteinfo["state"]==2:
                                reject=1
                   item["uuid"]=uuid
                   item["sendstatus"]=sendstatus
                   item["click"]=click
                   item["register"]=register
                   item["quote"]=quote
                   item["accept"]=accept
                   item["reject"]=reject
                   detail.append(item)
           query_str = {}
           query_str["id"] = pushid
           nav = {
               'model': 'stat/pushrecord/detail',
               'cur': page + 1,
               'num': num,
               'query': "%s" % urlencode(query_str)
           }
           self.render("record_detail.html",record=record,detail=detail,nav=nav)
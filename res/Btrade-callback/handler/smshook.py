# -*- coding: utf-8 -*
from utils import *
from config import *
from base import BaseHandler
from mongodb import PymongoDateBase
from globalconfig import *


class SmsHookHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        self.log.info(self.request.arguments)
        token = self.get_argument("token","")
        timestamp = self.get_argument("timestamp","")
        signature=self.get_argument("signature","")
        if verify(sms_hook_app_key, token, timestamp, signature):
            statusCode=self.get_argument("statusCode",0)
            templateId=self.get_argument("templateId",None)
            phone=self.get_argument("phone","")
            if templateId and templateId == "870":
                mongodb = PymongoDateBase.instance().get_db()
                colleciton = mongodb.push_record
                eventType=self.get_argument("eventType",None)
                if eventType == "2":
                    colleciton.update({'sendid': phone}, {'$set': {'sendstatus': 1}})
                if eventType in("4","5") :
                    colleciton.update({'sendid': phone}, {'$set': {'sendstatus': 2}})
                    if statusCode in('500','510','590'):#关机停机的用户
                        self.db.execute("update supplier set pushstatus=0 where mobile=%s",phone)
            self.api_response({'status': 'success', 'message': '成功接收消息'})
        else:
            self.api_response({'status': 'fail', 'message': '参数错误'})
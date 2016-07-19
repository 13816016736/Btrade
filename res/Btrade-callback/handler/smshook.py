# -*- coding: utf-8 -*
from utils import *
from config import *
from base import BaseHandler

class SmsHookHandler(BaseHandler):
    def get(self):
        pass

    def post(self):
        token = self.get_argument("token","")
        timestamp = self.get_argument("timestamp","")
        signature=self.get_argument("signature","")
        if verify(sms_hook_app_key, token, timestamp, signature):
            statusCode=self.get_argument("statusCode",0)
            phone=self.get_argument("phone","")
            if statusCode in('500','510','590'):#关机停机的用户
               if phone!="":
                   self.db.execute("update supplier set pushstatus=0 where mobile=%s",phone)
            self.api_response({'status': 'success', 'message': '成功接收消息'})
        else:
            self.api_response({'status': 'fail', 'message': '参数错误'})
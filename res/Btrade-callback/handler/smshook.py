# -*- coding: utf-8 -*
from utils import *
from config import *
from base import BaseHandler
from mongodb import PymongoDateBase
from globalconfig import *
from alipay import *

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


class AlipayNotifyHandler(BaseHandler):
    def post(self):
        self.log.info(self.request.arguments)
        params=self.request.arguments
        ks = params.keys()
        newparams = {}
        for k in ks:
            v = params[k][0]
            newparams[k]=v
        if notify_verify(newparams):
            tn = self.get_argument('out_trade_no')
            trade_no = self.get_argument('trade_no')
            trade_status = self.get_argument('trade_status')
            self.log.info("tn=%s,trade_no=%s,trade_status=%s",tn,trade_no,trade_status)

            if trade_status == 'TRADE_SUCCESS':#支付成功
                self.db.execute("update payment set status=%s,tradeno=%s where payid=%s",1,trade_no,tn)
            else:
                self.db.execute("update payment set status=%s,tradeno=%s where payid=%s",0, trade_no, tn)
            self.api_response("success")
        else:
            self.api_response("fail")

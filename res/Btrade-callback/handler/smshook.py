# -*- coding: utf-8 -*
from utils import *
from config import *
from base import BaseHandler
from mongodb import PymongoDateBase
from globalconfig import *
from alipay import *
import time
from wxpay import *

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
                self.db.execute("update payment set status=%s,tradeno=%s,callbacktime=%s where payid=%s",1,trade_no,int(time.time()),tn)
                payment=self.db.get("select * from payment where payid=%s",tn)
                if payment:
                    userid=payment["userid"]
                    status=payment["status"]
                    membertype=2
                    if payment.paytype == 1:
                        membertype=3
                    elif payment.paytype == 2:
                        membertype = 2
                    if status==1:
                        member = self.db.get("select * from member where userid=%s", userid)
                        if member==None:
                            self.db.execute(
                                "insert into member (userid,term,upgradetime,type,expiredtime) value(%s,%s,%s,%s,%s)",
                                userid, 0, int(time.time()),membertype,"")


            else:
                self.db.execute("update payment set status=%s,tradeno=%s,callbacktime=%s where payid=%s",2, trade_no,int(time.time()), tn)
            self.write("success")
        else:
            self.write("fail")

class WxpayNotifyHandler(BaseHandler):
    def post(self):
        """支付回调"""
        FAIL, SUCCESS = "FAIL", "SUCCESS"
        request = self.request
        xml=request.body
        # 使用通用通知接口
        notify = Notify_pub()
        notify.saveData(xml)
        self.log.info(xml)
        # 验证签名，并回应微信。
        # 对后台通知交互时，如果微信收到商户的应答不是成功或超时，微信认为通知失败，
        # 微信会通过一定的策略（如30分钟共8次）定期重新发起通知，
        # 尽可能提高通知的成功率，但微信不保证通知最终能成功
        if not notify.checkSign():
            notify.setReturnParameter("return_code", FAIL)  # 返回状态码
            notify.setReturnParameter("return_msg", "签名失败")  # 返回信息
        else:
            result = notify.getData()

            if result["return_code"] == FAIL:
                notify.setReturnParameter("return_code", FAIL)
                notify.setReturnParameter("return_msg", "通信错误")
            elif result["result_code"] == FAIL:
                notify.setReturnParameter("return_code", FAIL)
                notify.setReturnParameter("return_msg", result["err_code_des"])
            else:
                notify.setReturnParameter("return_code", SUCCESS)
                result_code= result["result_code"]
                out_trade_no = result["out_trade_no"]  # 商户系统的订单号，与请求一致。
                trade_no = result["transaction_id"]
                if result_code==SUCCESS:
                    self.db.execute("update payment set status=%s,tradeno=%s,callbacktime=%s where payid=%s",1,trade_no,int(time.time()),out_trade_no)
                    payment=self.db.get("select * from payment where payid=%s",out_trade_no)
                    if payment:
                        userid=payment["userid"]
                        status=payment["status"]
                        membertype=2
                        if payment.paytype == 1:
                            membertype=3
                        elif payment.paytype == 2:
                            membertype = 2
                        if status==1:
                            member = self.db.get("select * from member where userid=%s and type=%s", userid,membertype)
                            if member==None:
                                self.db.execute(
                                    "insert into member (userid,term,upgradetime,type,expiredtime) value(%s,%s,%s,%s,%s)",
                                    userid, 0, int(time.time()),membertype,"")
                else:
                    self.db.execute("update payment set status=%s,tradeno=%s,callbacktime=%s where payid=%s", 2, trade_no,int(time.time()), out_trade_no)

        self.write(notify.returnXml())

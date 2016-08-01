# -*- coding: utf-8 -*-

import tornado.web
import session
from database import database
import json
from  datetime import date,datetime
from producer import KafkaProduceServer
from globalconfig import *
import logging
from mongodb import PymongoDateBase
import time
import logging
class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)

def purchase_push_trace(method):#商品推送链接进入的路径路由
    def wrapper(self, *args, **kwargs):
         uuid = self.get_argument("uuid", None)  # 如果是从push的链接访问进来
         if uuid:
             self.session["uuid"] = uuid
             self.session.save()
         elif  self.session.get("uuid") :
            uuid=self.session.get("uuid")
         if uuid!=None:
            try:
                producer_server = KafkaProduceServer(analysis_send_topic, kafka_server)
                userid=self.session.get("userid")
                if userid==""or userid==None:
                    userid=-1
                mongodb = PymongoDateBase.instance().get_db()
                colleciton = mongodb.push_record
                record=colleciton.find_one({"uuid":uuid})
                if record:
                    quoteid=self.session.get("quoteid")
                    if quoteid:#报价之后取的quoteid:
                        self.session["quoteid"] = -1
                        self.session.save()
                    else:
                        quoteid=-1
                    producer_server.sendJson("data", {'uuid': uuid, "url": self.request.uri, "monitor_type": record["type"],
                                                      "method": self.request.method,"quoteid":quoteid, "userid": userid,"messagetype":1,"createtime":int(time.time())})
                producer_server.close()
            except Exception,ex:
                logger = logging.getLogger()
                logger.error("kafkaProduce send error(%s)"%str(ex))
         return method(self, *args, **kwargs)
    return wrapper

class WebBaseHandler(tornado.web.RequestHandler):
  
  def initialize(self):
      self.session = session.Session(self.application.session_manager, self)
      self.db = database.instance().get_session()
      self.log = logging.getLogger()

  def get(self):
      """捕获404"""
      self.send_error(404)

  def write_error(self, status_code, **kwargs):
      """重写404错误页
      """
      if status_code == 404:
          self.render('public/404.html')
      elif status_code == 500:
          self.render('public/500.html')
      else:
          self.write('error:' + str(status_code))

  def get_current_user(self):
       return None

  def success(self, message='操作成功', url=''):
        """操作成功提示
        """
        self.render('message/success.html', message=message, url=url)

  def failure(self, message="操作失败", url=''):
        self.render('message/failure.html', message=message, url=url)



  def api_response(self, data):
        """将数据转成json返回给客户端"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        data = json.dumps(data,cls=CJsonEncoder)
        self.finish(data)

  def on_finish(self):
      self.db.close()



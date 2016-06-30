# -*- coding: utf-8 -*-

import tornado.web
import session
from database import database
import json
from webbasehandler import WebBaseHandler


class BaseHandler(WebBaseHandler):

  def get_current_user(self):
       return self.session.get("user")


  def error(self, message="出现错误了", url=''):
        """操作失败提示
        """
        self.render('message/message.html', bool=False, message=message, url=url)

  def api_response(self, data):
        """将数据转成json返回给客户端"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        data = json.dumps(data)
        self.finish(data)

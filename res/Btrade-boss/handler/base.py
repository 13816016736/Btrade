# -*- coding: utf-8 -*-

import tornado.web
import session
from database import database
import json
from webbasehandler import WebBaseHandler


class BaseHandler(WebBaseHandler):
  def get_current_user(self):
       return self.session.get("admin")


  def error(self, message="出现错误了", url=''):
    """操作失败提示
    """
    self.render('message/error.html', message=message, url=url)



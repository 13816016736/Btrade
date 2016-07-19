# -*- coding: utf-8 -*-

import tornado.web
import session
from database import database
import json


class BaseHandler(tornado.web.RequestHandler):
  def initialize(self):
      self.session = session.Session(self.application.session_manager, self)
      self.db = database.instance().get_session()

  def api_response(self, data):
        """将数据转成json返回给客户端"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        data = json.dumps(data)
        self.finish(data)

  def get_current_user(self):
      return None

  def on_finish(self):
      self.db.close()


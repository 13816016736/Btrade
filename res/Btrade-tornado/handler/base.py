# -*- coding: utf-8 -*-

import tornado.web
import session
from database import database

class BaseHandler(tornado.web.RequestHandler):
  
  def initialize(self):
      self.session = session.Session(self.application.session_manager, self)
      self.db = database.instance().get_session()

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
       # return self.get_secure_cookie("user")
      return self.session.get("user")

  def success(self, message='操作成功', url=''):
        """操作成功提示
        """
        self.render('message/success.html', message=message, url=url)

  def failure(self, message="操作失败", url=''):
        self.render('message/failure.html', message=message, url=url)

  def error(self, message="出现错误了", url=''):
        """操作失败提示
        """
        self.render('message/error.html', message=message, url=url)

  def on_finish(self):
      self.db.close()
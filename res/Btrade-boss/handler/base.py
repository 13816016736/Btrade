# -*- coding: utf-8 -*-

import tornado.web
import session
from database import database
import json
from webbasehandler import WebBaseHandler


class BaseHandler(WebBaseHandler):
  def get_current_user(self):
       return self.session.get("admin")




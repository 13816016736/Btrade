#coding:utf8
import tornado.web
from base import BaseHandler
import os
import config
import time
import datetime
from utils import *

class IdentifyUserHandler(BaseHandler):
    def get(self):
        pass
    def post(self):
        self.api_response(
            {'status': 'success', 'message': '提交成功'})
        pass


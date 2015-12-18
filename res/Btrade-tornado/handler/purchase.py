# -*- coding: utf-8 -*-

import tornado.web
from base import BaseHandler
import json

class PurchaseHandler(BaseHandler):

    def get(self):
        provinces = self.db.query("SELECT id,areaname FROM area WHERE parentid = 0")
        self.render("purchase.html", provinces=provinces)

    def post(self):
        print "in..."
        data = json.loads(self.request.body)
        print data
        self.render("success.html", current_user=self.current_user)

class MyPurchaseHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("dashboard/mypurchase.html")

    def post(self):
        pass

class MyPurchaseInfoHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self, id):
        print id
        self.render("dashboard/mypurchaseinfo.html")

    def post(self):
        pass

class GetCityHandler(BaseHandler):

    def get(self):
        pass

    def post(self):
        provinceid = self.get_argument("provinceid")
        if provinceid == "":
            self.api_response({'status':'fail','message':'请选择省份'})
        else:
            cities = self.db.query("SELECT id,areaname FROM area WHERE parentid = %s", provinceid)
            self.api_response({'status':'success','message':'请求成功','data':cities})
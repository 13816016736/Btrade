import tornado.web
from base import BaseHandler

class PurchaseHandler(BaseHandler):

    def get(self):
        nav = {
            'model': 'index',
            'num': 58,
        }
        entries = self.db.query("SELECT * FROM weibo_users LIMIT 5")
        self.render("purchase.html", entries=entries, current_user=self.current_user, nav=nav, title="dsad")

    def post(self):
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
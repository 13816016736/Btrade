import tornado.web
from base import BaseHandler

class MainHandler(BaseHandler):
    #@tornado.web.authenticated
    def get(self):
        nav = {
            'model': 'index',
            'num': 58,
        }
        entries = self.db.query("SELECT * FROM weibo_users LIMIT 5")
        self.render("main.html", entries=entries, current_user=self.current_user, nav=nav, title="dsad")
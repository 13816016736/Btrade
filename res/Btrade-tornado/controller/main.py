import tornado.web
from base import BaseHandler

class MainHandler(BaseHandler):
    def get(self):
		entries = self.db.query("SELECT * FROM weibo_users LIMIT 5")
		self.render("../templates/test.html", entries=entries)  
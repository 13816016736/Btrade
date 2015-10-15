import tornado.web
from base import BaseHandler

class MainHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
	    entries = self.db.query("SELECT * FROM weibo_users LIMIT 5")
	    self.render("test.html", entries=entries, current_user=self.current_user)
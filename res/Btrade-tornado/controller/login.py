import tornado.web
from base import BaseHandler

class LoginHandler(BaseHandler):
    def get(self):
	    self.render("login.html", next_url=self.get_argument("next", "/"))

    def post(self):
        # self.set_secure_cookie("user", self.get_argument("username"))
        self.session["user"] = self.get_argument("username")
        self.redirect(self.get_argument('next_url', '/'))


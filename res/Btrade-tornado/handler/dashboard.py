import tornado.web
from base import BaseHandler

class DashboardHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("dashboard/main.html")
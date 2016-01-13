import tornado.web
from base import BaseHandler
import config

class MainHandler(BaseHandler):
    def get(self):
        self.render("main.html")

class UserListHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, page=0):
        page = (int(page) - 1) if page > 0 else 0
        nav = {
            'model': 'users/userlist',
            'num': self.db.execute_rowcount("SELECT * FROM users"),
        }
        users = self.db.query("SELECT * FROM users LIMIT %s,%s", page * config.conf['POST_NUM'], config.conf['POST_NUM'])
        self.render("userlist.html", users=users, nav=nav)

class UserInfoHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userid):
        user = self.db.get("SELECT * FROM users where id = %s", userid)
        self.render("userinfo.html", user=user)

class UserRecoverHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userid):
        self.db.execute("update users set status=1 where id = %s", userid)
        self.redirect('/users/userlist')

class UserRemoveHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, userid):
        self.db.execute("update users set status=0 where id = %s", userid)
        self.redirect('/users/userlist')
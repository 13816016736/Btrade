import tornado.web
import session
from database import database

class BaseHandler(tornado.web.RequestHandler):
  
  def initialize(self):
      self.session = session.Session(self.application.session_manager, self)
      self.db = database.instance().get_session()

  def get_current_user(self):
       # return self.get_secure_cookie("user")
      return self.session.get("user")

  def on_finish(self):
      self.db.close()
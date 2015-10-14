import tornado.web
from database import database

class BaseHandler(tornado.web.RequestHandler):
  
  def initialize(self):
      self.db = database.instance().get_session()

  def on_finish(self):
      self.db.close()
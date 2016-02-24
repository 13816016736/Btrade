from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from tornado.options import define, options

define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_db", default="easytalk", help="database name")
define("mysql_user", default="root", help="database user")
define("mysql_pass", default="", help="database password") 
define("mysql_poolsize", default=10, help="database password", type=int) 
define("debug", default=True, help="db mode") 

class database(object):
  def __init__(self):
    engine = create_engine("mysql://{0}:{1}@{2}/{3}".format(options.mysql_user, options.mysql_pass, options.mysql_host, options.mysql_db)
                            , pool_size = options.mysql_poolsize
                            , pool_recycle = 3600
                            , echo=options.debug
                            , echo_pool=options.debug)
    self._session = sessionmaker(bind=engine)
  
  @classmethod
  def instance(cls):
    """Singleton like accessor to instantiate backend object"""
    if not hasattr(cls,"_instance"):
      cls._instance = cls()
    return cls._instance
  
  def get_session(self):
    return self._session()
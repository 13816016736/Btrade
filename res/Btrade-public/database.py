import torndb
from tornado.options import define, options

define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_db", default="yaocai", help="database name")
define("mysql_user", default="yaocai", help="database user")
define("mysql_pass", default="ycg20160401", help="database password")
define("mysql_poolsize", default=10, help="database password", type=int) 
define("debug", default=True, help="db mode") 

class database(object):
  def __init__(self):
    self._session = torndb.Connection(  
            host = options.mysql_host,   
            database = options.mysql_db,   
            user = options.mysql_user,   
            password = options.mysql_pass  
        )
  
  @classmethod
  def instance(cls):
    """Singleton like accessor to instantiate backend object"""
    if not hasattr(cls,"_instance"):
      cls._instance = cls()
    return cls._instance
  
  def get_session(self):
    return self._session

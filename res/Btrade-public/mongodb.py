import pymongo
from globalconfig import *
class PymongoDateBase(object):
    def __init__(self):
        self._client = pymongo.MongoClient(mongodb_ip, mongodb_port)
        self._db=self._client[db_name]
    @classmethod
    def instance(cls):
        """Singleton like accessor to instantiate backend object"""
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def get_db(self):
        return self._db
    def close(self):
        self._client.close()

if __name__ == "__main__":
    #client = pymongo.MongoClient("localhost", 27017)
    client = PymongoDateBase.instance()
    db=client.get_db()
    import datetime
    my_colleciton= db.my_collection
    new_post = {"AccountID": 23, "UserName": "xccww", 'date': datetime.datetime.now()}
    my_colleciton.insert(new_post)
    #post= my_colleciton.find_one({"AccountID": 22})
    #dt=post["date"]
    #print dt.strftime("%Y/%m/%d %H:%M:%S")
    client.close()
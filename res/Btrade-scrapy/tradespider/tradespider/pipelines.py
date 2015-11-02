# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
from scrapy.exceptions import DropItem


class FilterWordsPipeline(object):
    """A pipeline for filtering out items which contain certain words in their
    description"""

    # put all words in lowercase
    words_to_filter = ['politics', 'religion']

    def process_item(self, item, spider):
        for word in self.words_to_filter:
            if word in unicode(item['description']).lower():
                raise DropItem("Contains forbidden word: %s" % word)
        else:
            return item

class JsonWriterPipeline(object):
    def __init__(self):
        self.file = codecs.open('items.json', 'w', encoding='utf-8')
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line.decode('unicode_escape'))
        return item

class TradespiderPipeline(object):
    def process_item(self, item, spider):
        return item



from twisted.enterprise import adbapi              #导入twisted的包
import MySQLdb
import MySQLdb.cursors
import sys

class MySQLStorePipeline(object):
    def __init__(self):                            #初始化连接mysql的数据库相关信息
        '''self.dbpool = adbapi.ConnectionPool('MySQLdb',
                db = 'purchase',
                user = 'root',
                passwd = '',
                cursorclass = MySQLdb.cursors.DictCursor,
                charset = 'utf8',
                use_unicode = False
        )'''
        self.conn = MySQLdb.connect(host='localhost',user='root',passwd='',db='purchase',port=3306, charset="utf8")
        self.cursor = self.conn.cursor()

    # pipeline dafault function                    #这个函数是pipeline默认调用的函数
    def process_item(self, item, spider):
        '''query = self.dbpool.runInteraction(self._conditional_insert, item)
        '''
        try:
            self.cursor.execute("insert into purchaseInfo values (%s, %s, %s, %s, %s, %s, %s)",
                           (item["title"], item["name"], item["specification"],
                         item["origin"], item["image"], item["price"], item["unit"]))

            self.conn.commit()
        except MySQLdb.Error, e:
            print "-----"
            print e
            print "-----"

        return item

    # insert the data to databases                 #把数据插入到数据库中
    '''def _conditional_insert(self, tx, item):
        sql = "insert into purchaseInfo values (%s, %s, %s, %s, %s, %s, %s)"
        tx.execute(sql, (item["title"], item["name"], item["specification"],
                         item["origin"], item["image"], item["price"], item["url"]))'''


class YaocaiMySQLStorePipeline(object):
    def __init__(self):                            #初始化连接mysql的数据库相关信息
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.conn = MySQLdb.connect(host='localhost',user='root',passwd='',db='purchase',port=3306, charset="utf8")
        self.cursor = self.conn.cursor()

    # pipeline dafault function                    #这个函数是pipeline默认调用的函数
    def process_item(self, item, spider):
        try:
            self.cursor.execute("insert into yaocai (type, name, alias, english, product, "
                                "origin, price, specification, identification, outline, "
                                "discourse, characters) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (item["type"], item["name"], item["alias"], item["english"], item["product"],
                            item["origin"], item["price"], item["specification"], item["identification"],
                            item["outline"], item["discourse"],
                            item["characters"]))
            yaocaiid = int(self.cursor.lastrowid)
            order = 0
            for image in item["images"]:
                order += 1
                self.cursor.execute("insert into images (yaocaiid, type, image, orderid) values (%s, %s, %s, %s)",
                               (yaocaiid, 1, image, order))
            order = 0
            for encyclopedias in item["encyclopedias"]:
                order += 1
                self.cursor.execute("insert into images (yaocaiid, type, image, orderid) values (%s, %s, %s, %s)",
                               (yaocaiid, 2, encyclopedias, order))
            order = 0
            for variety in item["variety"]:
                order += 1
                self.cursor.execute("insert into variety (yaocaiid, variety) values (%s, %s)",
                               (yaocaiid, variety))

            self.conn.commit()
        except MySQLdb.Error, e:
            print "-----"
            print e
            print "-----"

        return item



# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs
from scrapy.exceptions import DropItem
from datetime import timedelta,datetime
from time import strftime, localtime
import time

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

class ZyccstMySQLStorePipeline(object):
    def __init__(self):                            #初始化连接mysql的数据库相关信息
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.conn = MySQLdb.connect(host='localhost',user='root',passwd='ycg20160401',db='purchase',port=3306, charset="utf8")
        self.cursor = self.conn.cursor()

    # pipeline dafault function                    #这个函数是pipeline默认调用的函数
    def process_item(self, item, spider):
        try:
            # self.cursor.execute("insert into supplier (name, company, phone, mobile, qq, address, businessplace, "
            #                     "variety, addvariety, scale, sales, relationship, manager, source) "
            #                     "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            self.cursor.execute("select id from variety where name = %s", item["variety"])
            variety = self.cursor.fetchone()
            if variety and len(variety) == 1:
                varietyid = variety[0]
                self.cursor.execute("select id,variety from supplier where mobile = %s", item["mobile"])
                supplier = self.cursor.fetchone()
                if supplier:
                    supplier[1] = supplier[1]+","+varietyid
                    varietyids = ",".join(list(set(supplier[1].split(","))))
                    self.cursor.execute("update supplier set variety = %s where id = %s ", (varietyids, supplier[0]))
                else:
                    self.cursor.execute("insert into supplier (name, phone, mobile, qq, address, variety, source) "
                                        "values (%s, %s, %s, %s, %s, %s, %s)",
                                   (item["name"], item["phone"], item["mobile"], item["qq"], item["address"], varietyid, 'zyccst'))
                self.conn.commit()
        except MySQLdb.Error, e:
            print "-----"
            print e
            print "-----"

        return item


class YoBoPipeline(object):
    def __init__(self):  # 初始化连接mysql的数据库相关信息
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='ycg20160401', db='yaocai', port=3306,
                                    charset="utf8")
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        #主营品种可能有多个
        varieties=[]
        if item['variety'].find(" ")!=-1:
            varieties=item['variety'].split(" ")
            print varieties
        for var in varieties:
            try:
                self.cursor.execute("select id from variety where name = %s or alias=%s ",(var,var))
                variety = self.cursor.fetchone()
                if variety and len(variety) == 1:
                    varietyid = variety[0]
                    print varietyid
                    self.cursor.execute("select id,variety from supplier where mobile = %s limit 0,1"%(item["mobile"]))
                    supplier = self.cursor.fetchone()
                    if supplier:
                        if(supplier[1].find(str(varietyid))==-1):
                            varietyids = ",".join(list(set(supplier[1].split(","))))+','+str(varietyid)
                            print "update supplier set variety = %s where id = %s ", (varietyids, supplier[0])
                            self.cursor.execute("update supplier set variety = %s where id = %s ", (varietyids, supplier[0]))
                    else:
                        self.cursor.execute("insert into supplier (name, mobile, address, variety, source) "
                                        "values (%s, %s, %s, %s, %s)",
                                    (item["name"], item["mobile"], item["address"], varietyid, 'yobo360'))
                    self.conn.commit()
            except MySQLdb.Error, e:
                print "-----"
                print e
                print "-----"

        return item
class ZycPipeline(object):
    def __init__(self):  # 初始化连接mysql的数据库相关信息
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='ycg20160401', db='yaocai', port=3306,
                                    charset="utf8")
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        #主营品种可能有多个
        varieties = []
        varieties.append(item["variety"])
        for var in varieties:
            try:
                self.cursor.execute("select id from variety where name = %s or alias like '%%%s%%'", (var, var))
                variety = self.cursor.fetchone()
                if variety and len(variety) == 1:
                    varietyid = variety[0]
                    print varietyid
                    self.cursor.execute(
                        "select id,variety from supplier where mobile = %s limit 0,1" % (item["mobile"]))
                    supplier = self.cursor.fetchone()
                    if supplier:
                        if (supplier[1].find(str(varietyid)) == -1):
                            varietyids = ",".join(list(set(supplier[1].split(",")))) + ',' + str(varietyid)
                            print "update supplier set variety = %s where id = %s ", (varietyids, supplier[0])
                            self.cursor.execute("update supplier set variety = %s where id = %s ",
                                                (varietyids, supplier[0]))
                    else:
                        self.cursor.execute("insert into supplier (name, mobile,phone,company address, variety, source) "
                                            "values (%s, %s, %s, %s, %s)",
                                            (item["name"], item["mobile"], item["phone"], item["company"], item["address"], varietyid, 'zyczyc'))
                    self.conn.commit()
            except MySQLdb.Error, e:
                print "-----"
                print e
                print "-----"
class KmzywPipeline(object):
    def __init__(self):  # 初始化连接mysql的数据库相关信息
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='ycg20160401', db='yaocai', port=3306,
                                    charset="utf8")
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        #主营品种可能有多个
        varieties=[]
        if item['variety'].find(",") != -1:
            varieties = item['variety'].split(",")
            print varieties
        for var in varieties:
            print var
            try:
                self.cursor.execute("select id from variety where name = %s or find_in_set(%s,alias)" ,(var, var))
                variety = self.cursor.fetchone()
                if variety and len(variety) == 1:
                    varietyid = variety[0]
                    print varietyid
                    self.cursor.execute(
                        "select id,variety from supplier where mobile = %s limit 0,1" % (item["mobile"]))
                    supplier = self.cursor.fetchone()
                    if supplier:
                        if (supplier[1].find(str(varietyid)) == -1):
                            varietyids = ",".join(list(set(supplier[1].split(",")))) + ',' + str(varietyid)
                            print "update supplier set variety = %s where id = %s ", (varietyids, supplier[0])
                            self.cursor.execute("update supplier set variety = %s where id = %s ",
                                                (varietyids, supplier[0]))
                    else:
                        print "insert into supplier (name, mobile,company address, variety, source) values (%s, %s,%s, %s, %s, %s)"%(item["name"], item["mobile"], item["company"], item["address"], varietyid, 'Kmzyw')
                        self.cursor.execute("insert into supplier (name, mobile,company,address, variety, source) values (%s,%s,%s, %s, %s, %s)",
                                            (item["name"], item["mobile"], item["company"], item["address"], varietyid, 'Kmzyw'))
                    self.conn.commit()
            except MySQLdb.Error, e:
                print "-----"
                print e
                print "-----"
class ZycCsTPipeline(object):
    def __init__(self):  # 初始化连接mysql的数据库相关信息
        reload(sys)
        sys.setdefaultencoding('utf-8')
        self.conn = MySQLdb.connect(host='localhost', user='root', passwd='ycg20160401', db='yaocai', port=3306,
                                    charset="utf8")
        self.cursor = self.conn.cursor()
    def process_item(self, item, spider):
        #主营品种可能有多个
        varieties=[]
        if item['variety'].find(",") != -1:
            varieties = item['variety'].split(",")
            print varieties
        for var in varieties:
            print var
            try:
                self.cursor.execute("select id from variety where name = %s or find_in_set(%s,alias)" ,(var, var))
                variety = self.cursor.fetchone()
                if variety and len(variety) == 1:
                    varietyid = variety[0]
                    print varietyid
                    self.cursor.execute(
                        "select id,variety from supplier where mobile = %s limit 0,1" % (item["mobile"]))
                    supplier = self.cursor.fetchone()
                    if supplier:
                        if (supplier[1].find(str(varietyid)) == -1):
                            varietyids = ",".join(list(set(supplier[1].split(",")))) + ',' + str(varietyid)
                            print "update supplier set variety = %s where id = %s ", (varietyids, supplier[0])
                            self.cursor.execute("update supplier set variety = %s where id = %s ",
                                                (varietyids, supplier[0]))
                    else:
                        print "insert into supplier (name, mobile, address, variety, source) values (%s, %s,%s, %s, %s)"%(item["name"], item["mobile"], item["address"], varietyid, 'Kmzyw')
                        self.cursor.execute("insert into supplier (name, mobile,address, variety, source) values (%s,%s, %s, %s, %s)",
                                            (item["name"], item["mobile"], item["address"], varietyid, 'zyccst_sjhy'))
                    self.conn.commit()
            except MySQLdb.Error, e:
                print "-----"
                print e
                print "-----"


from openpyxl import Workbook

class WriteExclePipeline(object):
    def __init__(self):
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.append(['企业名称', '地址', '电话'])  # 设置表头


    def process_item(self, item, spider):  # 工序具体内容
        line = [item['name'], item['address'], item['mobile']]  # 把数据中每一项整理出来
        self.ws.append(line)  # 将数据以行的形式添加到xlsx中
        self.wb.save(u'爬取数据.xlsx')  # 保存xlsx文件
        return item


import MySQLdb
import MySQLdb.cursors
import sys

class PurchaseSQlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host='localhost',user='root',passwd='123456',db='yaocai',port=3306, charset="utf8")
        self.cursor = self.conn.cursor()

    # pipeline dafault function                    #这个函数是pipeline默认调用的函数
    def process_item(self, item, spider):
        year = strftime("%Y", localtime())
        month = strftime("%m", localtime())
        day = strftime("%d", localtime())
        format = "%Y-%m-%d"
        date_str = "%s-%s-%s" % (year, month, day)
        now = datetime.strptime(date_str, format)
        start_date = now - timedelta(days=3)
        int_end = int(time.mktime(now.timetuple()))
        int_start = int(time.mktime(start_date.timetuple()))

        publish_time = datetime.strptime(item["purchaseDate"], format)
        int_publish = int(time.mktime(publish_time.timetuple()))
        if int_publish<=int_end and int_publish>int_start:
            # 去重
            self.cursor.execute(
                "select * from trader_data where mobile ='%s' and variety='%s'" % (item["mobile"], item["variety"]))
            data_result = self.cursor.fetchall()
            if (len(data_result) == 0):
                try:
                    self.cursor.execute("insert into trader_data(name,mobile,purchaseDate,variety,spec,quantity,quality,origin,source)values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (item["name"], item["mobile"], item["purchaseDate"],
                             item["variety"], item["spec"], item["quantity"], item["quality"],item["origin"], 1))

                    self.conn.commit()
                except MySQLdb.Error, e:
                    print "-----"
                    print e
                    print "-----"

            return item
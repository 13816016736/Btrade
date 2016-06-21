# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
import sys

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
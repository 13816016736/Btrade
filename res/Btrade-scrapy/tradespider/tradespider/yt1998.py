# -*- coding: utf-8 -*-
import json
import MySQLdb

# conn = MySQLdb.connect(host='localhost',user='root',passwd='ycg20160401',db='purchase',port=3306, charset="utf8")
# cursor = conn.cursor()
#
# cursor.execute("select id,variety from supplier")
# supplier = cursor.fetchall()
# for s in supplier:
#     print s[1]
#     var = ",".join(list(set(s[1].split(","))))
#     print var
#     cursor.execute("update supplier set variety = %s where id = %s ", (var, s[0]))
# conn.commit()

with open("E:\\Btrade\\res\\Btrade-scrapy\\tradespider\\tradespider\\ytSupplyList.json", "r") as f:
    d1 = json.load(f)
    for data in d1["data"]:
        if data["ycnam"] == u'旱半夏':
            print data["ycnam"]
            conn = MySQLdb.connect(host='localhost',user='root',passwd='ycg20160401',db='purchase',port=3306, charset="utf8")
            cursor = conn.cursor()

            # cursor.execute("select id from variety where name = %s", (data["ycnam"],))
            # variety = cursor.fetchone()
            variety = [119]
            if variety and len(variety) == 1:
                varietyid = variety[0]
                cursor.execute("select id,variety from supplier where mobile = %s", (data["mob"],))
                supplier = cursor.fetchone()
                if supplier:
                    var = supplier[1]+","+str(varietyid)
                    varietyids = ",".join(list(set(var.split(","))))
                    cursor.execute("update supplier set variety = %s where id = %s ", (varietyids, supplier[0]))
                else:
                    cursor.execute("insert into supplier (name, mobile, qq, address, variety, source) "
                                        "values (%s, %s, %s, %s, %s, %s)",
                                   (data["unam"], data["mob"], data["qq"], data["addr"], varietyid, 'yt1998'))
                conn.commit()


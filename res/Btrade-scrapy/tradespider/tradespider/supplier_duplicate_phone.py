# -*- coding: utf-8 -*-
#去除一些不太合法的记录
import json
import MySQLdb

conn = MySQLdb.connect(host='localhost',user='root',passwd='ycg20160401',db='yaocai',port=3306, charset="utf8")
cursor = conn.cursor()

for i in range(0,10,1):
    start_num=i*1000
    cursor.execute("alter table supplier modify phone varchar(100) NOT NULL")
    cursor.execute("select * from supplier where source='zyccst' limit %d,1000"%start_num)
    supplier = cursor.fetchall()
    if(len(supplier)==0):
        break
    for s in supplier:
        name=s[1]
        mobil_num=s[4]
        qq=s[5]
        address=s[6]
        id=s[0]
        variety=s[8]
        phone_num=s[3]
        try:
            if mobil_num.find("400")==0 or mobil_num.find(u"转")!=-1:
                print mobil_num
                set_phone=mobil_num
                if(phone_num!=""):
                    set_phone = phone_num+","+set_phone
                print set_phone
                cursor.execute("update supplier set phone = %s where id = %s ", (set_phone, id))
                cursor.execute("update supplier set mobile= %s where id = %s ", ("", id))
            elif mobil_num.find(",")!=-1:
                mobiles=mobil_num.split(u",")
                if len(mobiles)>=2:
                    if(len(mobiles[0])==11):
                        cursor.execute("update supplier set mobile = %s where id = %s ", (mobiles[0], id))
                    for m in mobiles[1:]:
                        print m
                        if len(m)==11:
                            cursor.execute("insert into supplier (name, mobile, qq, address, variety, source) values ('%s', '%s', '%s', '%s', '%s', '%s')" %(name, m, qq, address, variety, 'zyccst'))

            elif mobil_num.find("/")!=-1:
                if len(mobiles)>=2:
                    if (len(mobiles[0]) == 11):
                        cursor.execute("update supplier set mobile = %s where id = %s ", (mobiles[0], id))
                    for m in mobiles[1:]:
                        print m
                        if len(m)==11:
                            cursor.execute("insert into supplier (name, mobile, qq, address, variety, source) values ('%s', '%s', '%s', '%s', '%s', '%s')" %(name, m, qq, address, variety, 'zyccst'))
            else:
                if (len(mobil_num) != 11):
                    cursor.execute("delete from supplier where id = %s"%id)
        except MySQLdb.Error, e:
            print "-----"
            print e
            print "-----"

conn.commit()
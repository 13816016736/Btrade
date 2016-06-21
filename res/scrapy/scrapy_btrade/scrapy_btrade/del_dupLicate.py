#coding:utf8
import MySQLdb
conn = MySQLdb.connect(host='localhost',user='root',passwd='ycg20160401',db='yaocai',port=3306, charset="utf8")
cursor = conn.cursor()
cursor.execute("delete from supplier where id not in (select * from (select id from supplier group by mobile,variety)b)")#删除mobile，variety完全重复的记录
#处理mobile重复的记录，合并variety
conn.commit()
cursor.execute("select mobile from supplier group by mobile HAVING count(*)>1")
supplier = cursor.fetchall()
for item in supplier:
    if(len(item[0])!=11):#去掉不合法手机号
        cursor.execute("delete from supplier where mobile = '%s'"% item[0])
        continue
    print item[0]
    cursor.execute("select id,mobile,variety from supplier where mobile=%s",(item[0],))
    duplicate_sup = cursor.fetchall()
    id=duplicate_sup[0][0]
    mobile=duplicate_sup[0][1]
    variety = duplicate_sup[0][2]
    for dup in duplicate_sup[1:]:
        dup_variety = dup[2]
        dup_id=dup[0]
        if(variety.find(dup_variety)==-1):
            varietyids = ",".join(list(set(variety.split(",")))) + ',' + str(dup_variety)
            print ("update supplier set variety = %s where id = %s ",(varietyids, id))
            cursor.execute("update supplier set variety = %s where id = %s ",(varietyids, id))
            print ("delete from supplier where id = %s ", (dup_id))
            cursor.execute("delete from supplier where id = %s" % dup_id)
        else:
            cursor.execute("delete from supplier where id = %s" % dup_id)



conn.commit()

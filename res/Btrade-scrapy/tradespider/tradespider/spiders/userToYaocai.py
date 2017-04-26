#coding:utf8
import MySQLdb
import MySQLdb.cursors
import time

def md5(str):
    import hashlib
    import types
    if type(str) is types.StringType:
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()
    else:
        return ''
if __name__ == '__main__':
    #连接yaocai
    conn_yaocai = MySQLdb.connect(host='localhost', user='yaocai', passwd='ycg20160401', db='yaocai', port=3306, charset="utf8")
    cursor_yaocai = conn_yaocai.cursor()

    #连接yaoyy
    conn_yaoyy = MySQLdb.connect(host='localhost', user='yaobest', passwd='yaobest20161110', db='yaoyy', port=3306, charset="utf8")
    cursor_yy = conn_yaoyy.cursor()
    yaocai_list=[]
    password="666666"
    salt="ycg20151012"
    n = cursor_yy.execute("select u.phone,u.openid,ud.name,ud.company,ud.area,ud.category_ids from user u left join user_detail ud on u.id=ud.user_id where u.openid is not NULL ")
    insert_num=0
    update_num=0
    for r in cursor_yy.fetchall():
        yaocai_item = {}
        yaocai_item["phone"] = r[0]
        yaocai_item["openid"]=r[1]
        yaocai_item["nickname"] = r[2]
        yaocai_item["company"] = r[3]
        yaocai_item["area"] = r[4]
        yaocai_item["variety"] = r[5]
        yaocai_list.append(yaocai_item)
    for item in yaocai_list:
        #修正varietyId
        if(item["variety"]!="" and item["variety"]!=None):
            variety_ids=item["variety"].split(",")
            yaocai_variety_ids=[]
            for var in variety_ids:
                cursor_yy.execute("select * from category where id=%s" % var)
                variety_result= cursor_yy.fetchall()
                if(len(variety_result)!=0):
                    variety_name=variety_result[0][2]
                    cursor_yaocai.execute("select *from variety where name='%s' or find_in_set('%s',alias)"%(variety_name,variety_name))
                    variety_yaocai_result=cursor_yaocai.fetchall()
                    if(len(variety_yaocai_result)!=0):
                        yaocai_variety_ids.append(str(variety_yaocai_result[0][0]))
            item["variety"]=",".join(yaocai_variety_ids)
        else:
            item["variety"] =""

        cursor_yaocai.execute("select id,openid,name from users where phone ='%s'" % item["phone"])
        mobile_result =cursor_yaocai.fetchall()
        print item
        if item["nickname"]==None:#去老供应商表去查是否有
            cursor_yaocai.execute("select name from supplier where mobile ='%s'" % item["phone"])
            supplier_result=cursor_yaocai.fetchall()
            if len(supplier_result)!=0:
                item["nickname"]=supplier_result[0][0]
        #users表不存在就插入
        if(len(mobile_result)==0):
            try:
                cursor_yaocai.execute(
                    "insert into users(username,password,type,phone,name,nickname,areaid,openid,varietyids,createtime)values (%s, %s,%s, %s,%s,%s,%s,%s,%s,%s)",
                    ("yyy" + time.strftime("%y%m%d%H%M%S"), md5(str(password + salt)),8,item["phone"],item["nickname"]if item["nickname"]!=None else "",item["nickname"]if item["nickname"]!=None else "",item["area"] if item["area"]!=None else 0 ,item["openid"],item["variety"],int(time.time())))

                conn_yaocai.commit()
                insert_num +=1
            except MySQLdb.Error, e:
                print "-----"
                print e
                print "-----"
        else:
            #修改openId
            userId = mobile_result[0][0]
            openId=mobile_result[0][1]
            name=mobile_result[0][2]
            if name=="" or name==None:
                if item["nickname"]!=None:
                    cursor_yaocai.execute(
                        "update users set name='%s' where id=%s" % (item["nickname"], userId))
                    cursor_yaocai.execute(
                        "update users set nickname='%s' where id=%s" % (item["nickname"], userId))
            if openId=="" or openId==None:
                cursor_yaocai.execute(
                    "update users set openid='%s' where id=%s" % (item["openid"], userId))
            conn_yaocai.commit()
            update_num+=1
            pass

    conn_yaoyy.close()
    conn_yaocai.close()
    print "insert_num="+str(insert_num)
    print "update_num=" + str(update_num)
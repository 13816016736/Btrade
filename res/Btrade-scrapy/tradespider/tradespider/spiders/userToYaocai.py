#coding:utf8
import MySQLdb
import MySQLdb.cursors
import time

if __name__ == '__main__':
    #连接yaocai
    conn_yaocai = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='yaocai', port=3306, charset="utf8")
    cursor_yaocai = conn_yaocai.cursor()

    #连接yaoyy
    conn_yaoyy = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='yaoyy', port=3306, charset="utf8")
    cursor_yy = conn_yaoyy.cursor()
    yaocai_list=[]
    n = cursor_yy.execute("select u.phone,ud.nickname,ud.company,ud.area,ud.type from user u left join user_detail ud on u.id=ud.user_id where u.source!=1 ")
    for r in cursor_yy.fetchall():
        yaocai_item = {}
        yaocai_item["phone"] = r[0]
        yaocai_item["nickname"] = r[1]
        yaocai_item["company"] = r[2]
        yaocai_item["area"] = r[3]
        yaocai_item["type"] = r[4]
        yaocai_list.append(yaocai_item)
    for item in yaocai_list:
        cursor_yaocai.execute("select * from users where phone ='%s'" % item["phone"])
        mobile_result =cursor_yaocai.fetchall()
        #users表不存在就插入
        if(len(mobile_result)==0):
            try:
                cursor_yaocai.execute(
                    "insert into users(username,password,type,phone,name,nickname,areaid,createtime)values (%s, %s,%s, %s,%s,%s,%s,%s)",
                    ("ycg" + time.strftime("%y%m%d%H%M%S"), "",item["type"] if (item["type"]!=None and item["type"]!=0) else 8,item["phone"],item["company"] if item["company"]!=None else "",item["nickname"]if item["nickname"]!=None else "药优优用户",item["area"] if item["area"]!=None else 0 ,int(time.time())))

                conn_yaocai.commit()
            except MySQLdb.Error, e:
                print "-----"
                print e
                print "-----"

    conn_yaoyy.close()
    conn_yaocai.close()
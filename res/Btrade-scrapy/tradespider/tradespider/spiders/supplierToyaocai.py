#coding:utf8
import MySQLdb
import MySQLdb.cursors

if __name__ == '__main__':
    #连接yaocai
    conn_yaocai = MySQLdb.connect(host='localhost', user='yaocai', passwd='ycg20160401', db='yaocai', port=3306, charset="utf8")
    cursor_yaocai = conn_yaocai.cursor()

    #连接yaoyy
    conn_yaoyy = MySQLdb.connect(host='localhost', user='yaobest', passwd='yaobest20161110', db='yaoyy', port=3306, charset="utf8")
    cursor_yy = conn_yaoyy.cursor()
    yaocai_list=[]
    n = cursor_yy.execute("select name,phone,address,area,enter_category,company,status,source from supplier")
    for r in cursor_yy.fetchall():
        yaocai_item = {}
        yaocai_item["name"]=r[0]
        yaocai_item["mobile"] = r[1]
        yaocai_item["adress"] = r[2]
        yaocai_item["area"] = r[3]
        yaocai_item["variety"] = r[4]
        yaocai_item["company"] = r[5]
        yaocai_item["status"] = r[6]
        yaocai_item["source"] = r[7]
        yaocai_list.append(yaocai_item)

    for item in yaocai_list:
        # 修正area值为两个
        area_code=[]
        area=item["area"]
        if area!="" and area!=None:
            cursor_yy.execute("select * from area where id=%s"%area)
            result=cursor_yy.fetchall()
            if(len(result)!=0):
                city=result[0][2]
                area_code.append(str(city))
                cursor_yy.execute("select * from area where id=%s"%city)
                city_result=cursor_yy.fetchall()
                if (len(city_result) != 0):
                    province= city_result[0][2]
                    area_code.append(str(province))
            item["area"]=",".join(area_code)
        else:
            item["area"] =""
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
        cursor_yaocai.execute("select * from supplier where mobile ='%s'" % item["mobile"])
        mobile_result =cursor_yaocai.fetchall()
        #供应商表不存在就插入
        if item["source"]==None:
            item["source"]=1
        if(len(mobile_result)==0 and item["variety"]!=""):
            try:
                cursor_yaocai.execute(
                    "insert into supplier(name,mobile,address,phone,businessplace,variety,company,source,sponsor,yaoyy_status)values (%s, %s, %s,%s, %s, %s,%s, %s,%s,%s)",
                    (item["name"], item["mobile"], item["adress"] if  item["adress"]!=None else "","",
                     item["area"], item["variety"], item["company"] if item["company"]!=None else "","yaoyy_"+str(item["source"]),"",item["status"]))

                conn_yaocai.commit()
            except MySQLdb.Error, e:
                print "-----"
                print item
                print e
                print "-----"
    conn_yaoyy.close()
    conn_yaocai.close()
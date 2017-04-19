#coding:utf8
import MySQLdb
import MySQLdb.cursors
import random
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
def get_purchaseid():
    rand = ''.join(random.sample(['0','1','2','3','4','5','6','7','8','9'], 2))
    return int(str(int(time.time())) + rand)

if __name__ == '__main__':
    #连接yaocai
    conn_yaocai = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='yaocai', port=3306, charset="utf8")
    cursor_yaocai = conn_yaocai.cursor()

    salt="ycg20151012"


    purchase_list=[]
    n = cursor_yaocai.execute("select * from trader_data where status=0 and source=2 limit 10 ")
    for r in cursor_yaocai .fetchall():
        purchase_item= {}
        purchase_item["id"]=r[0]
        purchase_item["name"]=r[1]
        purchase_item["mobile"] = r[2]
        purchase_item["variety"] = r[4]
        purchase_item["spec"] = r[5]
        purchase_item["quantity"] = r[6]
        purchase_item["quality"] = r[7]
        purchase_item["origin"]=r[8]
        purchase_item["source"]=r[9]
        purchase_list.append(purchase_item)
    for item in purchase_list:
        cursor_yaocai.execute("select id from users where phone ='%s'" % item["mobile"])
        mobile_result = cursor_yaocai.fetchall()
        userId=None
        print item["mobile"][-6:]
        if len(mobile_result)!=0:#存在
            userId=mobile_result[0][0]
        else:
            try:
                cursor_yaocai.execute(
                    "insert into users(username,password,type,phone,name,nickname,createtime)values (%s, %s,%s, %s,%s,%s,%s)",
                    ("ycg" + time.strftime("%y%m%d%H%M%S"), md5(str(item["mobile"][-6:] +salt)),8,item["mobile"],"",item["name"] ,int(time.time())))

                conn_yaocai.commit()
            except MySQLdb.Error, e:
                print "-----"
                print e
                continue
                print "-----"

            cursor_yaocai.execute("select id from users where phone ='%s'" % item["mobile"])
            mobile_result = cursor_yaocai.fetchall()
            if len(mobile_result) != 0:  # 存在
                userId = mobile_result[0][0]
        cursor_yaocai.execute(
            "select *from variety where name='%s' or find_in_set('%s',alias)" % (item["variety"], item["variety"]))
        variety_yaocai_result = cursor_yaocai.fetchall()
        if (len(variety_yaocai_result) != 0):
            item["varietyId"]=variety_yaocai_result[0][0]
        else:
            continue
        if item["source"]==1:
            if item["quantity"].find(u"吨")!=-1:
                item['nQuantity']=item["quantity"][0:-1]
                item['nUnit']="吨"
            elif item["quantity"].find(u"公斤")!=-1:
                item['nQuantity']=item["quantity"][0:-3]
                item['nUnit']=u"公斤"
            else:
                item['nQuantity']=1000
                item['nUnit']=u"公斤"
        else:
            if item["quantity"].isdigit():
                item['nQuantity'] = item["quantity"]
                item['nUnit'] = u"公斤"
            else:
                item['nQuantity']=1000
                item['nUnit']=u"公斤"
        try:
            purchaseid = get_purchaseid()
            cursor_yaocai.execute("insert into purchase (id, userid, areaid, invoice, pay, payday, payinfo,"
                           " send, receive, accept, other, supplier, remark, limited, term, createtime)"
                           "value(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (purchaseid, userId , 0, 0, 0,
                            0, "", 0, "",
                            "", "", 0,"", 0,
                            0, int(time.time())))

            cursor_yaocai.execute("insert into purchase_info (purchaseid, varietyid, name, specification, quantity, unit,"
                               " quality, origin, price,shine)value(%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                               (purchaseid, item["varietyId"], item['variety'], item['spec'],
                                item['nQuantity'], item['nUnit'],
                                item["quality"],
                                item["origin"], 0, 0))

            conn_yaocai.commit()
        except MySQLdb.OperationalError, e:
            conn_yaocai.commit().rollback()
            print (e.args[1], e.args[0])
        time.sleep(1)
        try:
            cursor_yaocai.execute("update trader_data set status=1 where id=%s"%(item["id"]))
            conn_yaocai.commit()
        except MySQLdb.Error, e:
            print "-----"
            print e
            continue
            print "-----"
    conn_yaocai.close()


#coding:utf8
import requests
import MySQLdb
import MySQLdb.cursors
import time
from time import strftime, localtime
from datetime import timedelta,datetime
#把当天的采购单加入表
if __name__ == '__main__':
    url = 'http://www.yt1998.com/ytw/second/gongqiu/getSupplyList.jsp'
    conn = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='yaocai', port=3306, charset="utf8")
    cursor = conn.cursor()
    index = 0
    year = strftime("%Y", localtime())
    month = strftime("%m", localtime())
    day = strftime("%d", localtime())
    format = "%Y-%m-%d"
    date_str = "%s-%s-%s" % (year, month, day)
    now= datetime.strptime(date_str, format)
    start_date=now -timedelta(days=3)
    int_end= int(time.mktime(now.timetuple()))
    int_start=int(time.mktime(start_date.timetuple()))



    while(1):
        param = {
            'gqflg': 1,
            'pageIndex': index,
            'pageSize': 10,
            'order_by':1
        }

        res = requests.get(url,param)
        data=res.json()["data"]
        for item in data:
            print item["dtm"]
            publish_time = datetime.strptime(item["dtm"], format)
            int_publish=int(time.mktime(publish_time.timetuple()))
            if int_publish<=int_end and int_publish>int_start:
                #去重
                cursor.execute("select * from trader_data where mobile ='%s' and variety='%s'" %(item["mob"],item["ycnam"]))
                data_result=cursor.fetchall()
                if(len(data_result)==0):
                    try:
                        cursor.execute(
                            "insert into trader_data(name,mobile,purchaseDate,variety,spec,quantity,quality,origin,source)values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (item["unam"], item["mob"], item["dtm"],
                            item["ycnam"], item["guige"], item["shul"], "", item["chandi"], 2))

                        conn.commit()
                    except MySQLdb.Error, e:
                        print "-----"
                        print e
                        print "-----"
        if(len(data)<10):
            break
        index+=1



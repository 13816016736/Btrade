import requests
import MySQLdb
import MySQLdb.cursors
if __name__ == '__main__':
    url = 'http://www.yt1998.com/ytw/second/gongqiu/getSupplyList.jsp'
    conn = MySQLdb.connect(host='localhost', user='root', passwd='123456', db='yaocai', port=3306, charset="utf8")
    cursor = conn.cursor()
    index = 427
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
            print item
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



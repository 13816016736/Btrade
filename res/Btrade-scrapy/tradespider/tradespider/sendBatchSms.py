#coding:utf8
from xlrd import open_workbook
from itertools import islice
import urllib
import httplib

#创建一个用于读取sheet的生成器,依次生成每行数据,row_count 用于指定读取多少行, col_count 指定用于读取多少列
def readsheet(s, row_count=-1, col_count=-1):#
    # Sheet 有多少行
    nrows = s.nrows
    # Sheet 有多少列
    ncols = s.ncols
    row_count = (row_count if row_count > 0 else nrows)
    col_count = (col_count if col_count > 0 else ncols)
    row_index = 0
    while row_index < row_count:
        yield [s.cell(row_index, col).value for col in xrange(col_count)]
        row_index += 1

#批量发送接口
def send_sms(apikey, text, mobile):
    #服务地址
    sms_host = "sms.yunpian.com"
    #端口号
    port = 443
    #版本号
    version = "v2"
    #智能匹配模板短信接口的URI
    sms_send_uri = "/" + version + "/sms/batch_send.json"
    params = urllib.urlencode({'apikey': apikey, 'text': text, 'mobile':mobile})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPSConnection(sms_host, port=port, timeout=30)
    conn.request("POST", sms_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str

if __name__ == '__main__':
    wb = open_workbook(u'短信群发名单.xlsx')  # 打开Excel文件
    phoneList=[]
    for s in wb.sheets():
        for row in islice(readsheet(s), 2,None):
            phone=str(int(row[8]))
            phoneList.append(phone)
    print ",".join(phoneList)
    print send_sms("","",",".join(phoneList))
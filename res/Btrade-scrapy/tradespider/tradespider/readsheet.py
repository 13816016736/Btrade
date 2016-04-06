# -*- coding: utf-8 -*-
from xlrd import open_workbook
from database import database

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

wb = open_workbook('E:\\Btrade\\res\\east20160309.xlsx') #打开Excel文件
# 读取Excel中所有的Sheet
index = 0
db = database.instance().get_session()
values = []
types={
    "根茎类": 1,
    "果实类": 2,
    "全草类": 3,
    "花叶类": 4,
    "树脂类": 5,
    "菌藻类": 6,
    "树皮类": 7,
    "藤木类": 8,
    "加工类": 9,
    "动物类": 10,
    "矿物类": 11,
    "香料类": 12,
    "其他": 13
}
for s in wb.sheets():
    for row in readsheet(s, 867, 7):# 只读取每个Sheet的前10行，前10列(当然你要确保,你的数据多余10行，且多余10列)
        if index > 0:
            #解析数据
            row[1] = types[row[1].encode("utf-8")]
            values.append(row[1:])
            print row
        index += 1
    #入库
    sql = "INSERT INTO `variety` (`type`, `name`, `specification`, `origin`, `alias`, `unit`) VALUES(%s, %s, %s, %s, %s, %s)"
    db.executemany(sql, values)
    db.close()
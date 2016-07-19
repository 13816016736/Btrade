# -*- coding: utf-8 -*-
import os.path


#显示设置
app = {
    #应用名称
    'name': '药采购',
    #应用附加信息(简短的说明)
    'title': '药材买卖的专业助手',
    #联系邮箱
    'email': '2011zhouhang@gmail.com',
}



#用户密码的salt
salt = "ycg20151012"

#图片服务器域名
img_domain = "http://static.yaocai.pro/"
#img_path = "E:\\wamp\\www\\static\\uploadfiles\\"
img_path = "/opt/resources/static/uploadfiles"
host = "http://m.yaocai.pro"

unit = "公斤"

appid = "wx90e04052c49aa63e"
secret = "b1146d3ec7e0a8a483064406f361a07b"
token = ""

usertype={
    1:"饮片厂",
    2:"药厂",
    3:"药材经营公司",
    4:"个体经营户",
    5:"合作社",
    6:"种植基地",
    7:"其他",
    8:"个人经营",
    9:"采购经理",
    10:"销售经理"
}

#爬虫爬的网站的对应代码
spider_net={
    "Kmzyw":"康美",
    "yobo360":"药博",
    "yt1998":"药通网",
    "zyccst":"诚实通",
    "zyccst_sjh":"诚实通",
    "zyczyc":"东方"
}
#自己录入和自主注册的
source_code={
    "manual_record":"人工录入",
    "manual_recommend":"人工推荐",
    "self_recommend":"自主推荐",
    "self_register":"自主注册"
}

analysis_send_topic="push_monitor"#推送分析的topic
kafka_server="localhost:9092"#kafka服务ip以及端口
zk_server="localhost:2181"
mongodb_ip="127.0.0.1"
mongodb_port=27017
db_name="yaocai_statistical"
monitor_type={
    "1":"短信渠道",
    "2":"微信渠道"
}
message_type={
    "1": "监控用户点击",
}
sms_hook_app_key="xaa50do4-akgg-zlzw-bugb-dq727c867d"

supplier_push_status={
    "1":"默认",
    "0":"不予推送",
    "2":"转化为用户"
}
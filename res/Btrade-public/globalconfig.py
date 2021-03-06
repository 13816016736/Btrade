# -*- coding: utf-8 -*-
import os.path


#显示设置
app = {
    #应用名称
    'name': '药优优',
    #应用附加信息(简短的说明)
    'title': '药材买卖的专业助手',
    #联系邮箱
    'email': '2011zhouhang@gmail.com',
}



#用户密码的salt
salt = "ycg20151012"

#图片服务器域名
img_domain = "http://static.yaobest.com/"
#img_domain="http://127.0.0.1:8089/"

#img_path = "E:/wamp/www/static/uploadfiles/"
img_path = "/opt/resources/static/uploadfiles"
host = "http://m.yaobest.com"

unit = "公斤"

appid = "wx0b6c6683f64d3cc2"
secret = "b52e6a9abba43685cf273c6028aec69d"
token = ""

#purchase_appid="wx27d7d93c3eeb22d0"
#purchase_secret="a580e8f5259f3019113c79f23b8763b9"

purchase_appid="wx0b6c6683f64d3cc2"
purchase_secret="b52e6a9abba43685cf273c6028aec69d"


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
suppliertype={
    1:"药材种植户",
    2:"合作社",
    3:"中间商",
    4:"饮品厂",
    5:"中药厂"
}
membertype={
    0:"普通会员",
    1 :"实力供货商",
    2:"阳光速配（供货商)",
    3:"阳光速配（采购商）"
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
    "self_register":"自主注册",
    "yaoyy_1":"药优优同步 - 系统录入",
    "yaoyy_2":"药优优同步 - 沪谯导入",
    "yaoyy_3":"药优优同步 - 天济导入",
    "yaoyy_4":"药优优同步 - 微信登记",

}

analysis_send_topic="push_monitor"#推送分析的topic
send_task_topic="send_task"#推送任务topic
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
task_type={
    "1":"采购单推送",
    "2":"采购单回复提醒"
}

#支付宝配置
ALIPAY_PARTNER="2088421705597170"
ALIPAY_KEY="f2zg8m8duuguxu9n87bnhm8263v4u7q5"
ALIPAY_INPUT_CHARSET = 'utf-8'
ALIPAY_SIGN_TYPE = 'MD5'
_GATEWAY = 'https://mapi.alipay.com/gateway.do?'
ALIPAY_RETURN_URL="http://www.yaobest.com/alipay/return"#同步通知
ALIPAY_NOTIFY_URL="http://cb.yaobest.com/alipay/notify"#异步通知

pay_type={
    1:"阳光匹配（采购商）保证金",
    2:"阳光匹配（供货商）保证金",
}
pay_mode={
    1:"支付宝支付",
    2:"微信支付"
}
pay_status={
    0:"未支付",
    1:"支付成功",
    2:"支付失败",
}

#保证金额
deposit=5000
sdeposit=3000
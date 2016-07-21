# -*- coding:utf-8 -*-


#发送引擎配置
#最大推送次数
max_push_time=5
#点击率低于这个数值，会继续推送直到最大推送次数
click_rate=0.5
#报价率低于这个数值，会继续推送直到最大推送次数
quote_rate=0.2
#拒绝报价率高于这个数值，会继续推送直到最大推送次数
reject_quote_rate=0.6

#回复率低于这个数值，会推送提醒
reply_rate=0.3

#距离短信推送时间，单位天
notify_days=1

#最大提醒次数
max_notify_time=2

#单次发送的最多号码个数
max_phone_num=20

#单次发送的最多微信个数
max_wx_num=20
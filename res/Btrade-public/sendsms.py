# -*- coding: utf-8 -*-
import requests
import json
import urllib
import time
from hashlib import md5
import logging

SMS_USER = 'ycg20151012'
SMS_KEY = 'tNznTmJ27Fl0kvIvCZlVthQjazjZHe4W'

def generate_md5(fp):
    m = md5()    
    m.update(fp)
    return m.hexdigest()

def send(templateId, phone, vars):
    # #除注册验证码之外的短信都不发
    # #2017/01/10
    # if templateId!=776:
    #     return ""



    url = 'http://sendcloud.sohu.com/smsapi/send'

    param = {
        'smsUser': SMS_USER,
        'templateId' : templateId,
        'phone' : phone,
        'vars' : vars
    }

    param_keys = list(param.keys())
    param_keys.sort()

    param_str = ""
    for key in param_keys:
        param_str += key + '=' + str(param[key]) + '&'
    param_str = param_str[:-1]

    sign_str = SMS_KEY + '&' + param_str + '&' + SMS_KEY
    sign = generate_md5(sign_str)

    param['signature'] = sign

    res = requests.post(url,data=param)
    return res.text

def sendx(templateId, tos):
    url = 'http://sendcloud.sohu.com/smsapi/sendx'
    # if templateId!=776:
    #     return ""
    param = {
        'smsUser': SMS_USER,
        'templateId' : templateId,
        'msgType' : 0,
        'tos' : tos
    }

    param_keys = list(param.keys())
    param_keys.sort()

    param_str = ""
    for key in param_keys:
        param_str += key + '=' + str(param[key]) + '&'
    param_str = param_str[:-1]

    sign_str = SMS_KEY + '&' + param_str + '&' + SMS_KEY
    sign = generate_md5(sign_str)

    param['signature'] = sign

    res = requests.post(url,data=param)

    return res.text

if __name__ == '__main__':
    templateId = 5641
    phone = 18971437973
    vars = '{}'
    print send(templateId, phone, vars)
    # sendx()
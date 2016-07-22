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
    logger = logging.getLogger()
    logger.info("pushPurchase sendx method  start")
    url = 'http://sendcloud.sohu.com/smsapi/sendx'

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

    logger.info("pushPurchase sendx method  param=%s",param)

    res = requests.post(url,data=param)

    logger.info("pushPurchase sendx method  post res=%s", res)

    return res.text

if __name__ == '__main__':
    templateId = 776
    phone = 15002781007
    vars = '{"%code%":"123456"}'
    send(templateId, phone, vars)
    # sendx()
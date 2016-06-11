# -*- coding: utf-8 -*-
import requests, config, json

def sendwx(templateId, openid, link, data):
    if openid:
        #先获取access_token
        accesstoken_url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (config.appid, config.secret)
        res = requests.get(accesstoken_url)
        message = json.loads(res.text.encode("utf-8"))
        access_token = message.get("access_token", None)
        if access_token:
            url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % (access_token)
            headers = {'content-type': 'application/json'}
            param = {
                'touser': openid,
                'template_id' : templateId,
                'url' : link,
                'data' : data
            }

            res = requests.post(url,data=json.dumps(param), headers=headers)
            return res.text
        else:
            return
    else:
        return

if __name__ == '__main__':
    templateId = 'RGAztJ6ocuwvJosRCsCCJd8imGif6TT8B7vXYPa_KGs'
    openid = 'oTEeNwbhIWPqSJ_japnmKJulYD7M'
    link = "m.yaocai.pro"
    data = {
        "first": {
           "value":"报价成功",
           "color":"#173177"
        },
        "keyword1":{
           "value":"黄连",
           "color":"#173177"
        },
        "keyword2": {
           "value":"对梁坤的黄连进行报价",
           "color":"#173177"
        },
        "keyword3": {
           "value":"12元/吨",
           "color":"#173177"
        },
        "keyword4": {
            "value": "2016/6/8",
            "color": "#173177"
        },
        "remark":{
           "value":"点击查看详情",
           "color":"#173177"
        }
    }
    sendwx(templateId, openid, link, data)
#coding:utf-8
import json
import time
import random
import hashlib
from urllib import quote
import xml.etree.ElementTree as ET
from alipay import smart_str
import urllib2

class WxPayConf_pub(object):
    """配置账号信息"""

    # =======【基本信息设置】=====================================
    # 微信公众号身份的唯一标识。审核通过后，在微信发送的邮件中查看
    APPID = "wx90e04052c49aa63e"
    # JSAPI接口中获取openid，审核后在公众平台开启开发模式后可查看
    APPSECRET = "b1146d3ec7e0a8a483064406f361a07b"
    # 受理商ID，身份标识
    MCHID = "1383646002"
    # 商户支付密钥Key。审核通过后，在微信发送的邮件中查看
    KEY = "48888888888888888888888888888886"

    # =======【异步通知url设置】===================================
    NOTIFY_URL = "http://1e950475.ngrok.io/payback"

    # =======【JSAPI路径设置】===================================
    JS_API_CALL_URL = "http://1e950475.ngrok.io/payment"

    #jsapi




class Common_util_pub(object):
    """所有接口的基类"""

    def trimString(self, value):
        if value is not None and len(value) == 0:
            value = None
        return value

    def createNoncestr(self, length = 32):
        """产生随机字符串，不长于32位"""
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        strs = []
        for x in range(length):
            strs.append(chars[random.randrange(0, len(chars))])
        return "".join(strs)

    def formatBizQueryParaMap(self, paraMap, urlencode):
        """格式化参数，签名过程需要使用"""
        slist = sorted(paraMap)
        buff = []
        for k in slist:
            v = quote(paraMap[k]) if urlencode else paraMap[k]
            buff.append("{0}={1}".format(k, smart_str(v)))

        return "&".join(buff)

    def getSign(self, obj):
        """生成签名"""
        #签名步骤一：按字典序排序参数,formatBizQueryParaMap已做
        String = self.formatBizQueryParaMap(obj, False)
        #签名步骤二：在string后加入KEY
        String = "{0}&key={1}".format(String,WxPayConf_pub.KEY)
        #签名步骤三：MD5加密
        String = hashlib.md5(String).hexdigest()
        #签名步骤四：所有字符转为大写
        result_ = String.upper()
        return result_


    def arrayToXml(self, arr):
        """array转xml"""
        xml = ["<xml>"]
        for k, v in arr.iteritems():
            if v.isdigit():
                xml.append("<{0}>{1}</{0}>".format(k, v))
            else:
                xml.append("<{0}>{1}</{0}>".format(k, smart_str(v)))
        xml.append("</xml>")
        return "".join(xml)


    def xmlToArray(self, xml):
        """将xml转为array"""
        array_data = {}
        root = ET.fromstring(xml)
        for child in root:
            value = child.text
            array_data[child.tag] = value
        return array_data




class JsApi_pub(Common_util_pub):
    """JSAPI支付——H5网页端调起支付接口"""

    parameters = None  # jsapi参数，格式为json
    prepay_id = None  # 使用统一支付接口得到的预支付id


    def setPrepayId(self, prepayId):
        """设置prepay_id"""
        self.prepay_id = prepayId



    def getParameters(self):
        """设置jsapi的参数"""
        jsApiObj = {}
        jsApiObj["appId"] = WxPayConf_pub.APPID
        timeStamp = int(time.time())
        jsApiObj["timeStamp"] = "{0}".format(timeStamp)
        jsApiObj["nonceStr"] = self.createNoncestr()
        jsApiObj["package"] = "prepay_id={0}".format(self.prepay_id)
        jsApiObj["signType"] = "MD5"
        jsApiObj["paySign"] = self.getSign(jsApiObj)
        self.parameters = json.dumps(jsApiObj)
        return self.parameters

class UnifiedOrder_pub(Common_util_pub):
    #统一支付参数
    parameters = None  # jsapi参数，格式为json
    body=""
    tn=""
    total_fee=0
    spbill_create_ip=""

    def __init__(self, body,tn,total_fee,spbill_create_ip):
        self.body=body
        self.tn=tn
        self.total_fee=total_fee
        self.spbill_create_ip=spbill_create_ip




    def getParameters(self):
        """设置jsapi的参数"""
        ApiObj = {}
        ApiObj["appId"] = WxPayConf_pub.APPID
        ApiObj["mch_id"] = WxPayConf_pub.MCHID
        ApiObj["nonce_str"] = self.createNoncestr()
        ApiObj["body"] =self.body
        ApiObj["out_trade_no"] =self.tn
        ApiObj["total_fee"] =self.total_fee
        ApiObj["spbill_create_ip"] =self.spbill_create_ip
        ApiObj["trade_type"]="JSAPI"
        ApiObj["notify_url"] = WxPayConf_pub.NOTIFY_URL
        ApiObj["sign"]=self.getSign(ApiObj)
        self.parameters=ApiObj
        xml='''
        <xml>
        <appid>%s</appid>
        <body>%s</body>
        <mch_id>%s</mch_id>
        <nonce_str>%s</nonce_str>
        <notify_url>%s</notify_url>
        <openid>%s</openid>
        <out_trade_no>%s</out_trade_no>
        <spbill_create_ip>%s</spbill_create_ip>
        <total_fee>%s</total_fee>
        <trade_type>%s</trade_type>
        <sign>%s</sign>
        </xml>
        '''%(ApiObj["appId"],ApiObj["body"],ApiObj["mch_id"],ApiObj["nonce_str"],ApiObj["notify_url"])
        return xml


class UrllibClient(object):
    """使用urlib2发送请求"""

    def get(self, url, second=30):
        return self.postXml(None, url, second)

    def postXml(self, xml, url, second=30):
        """不使用证书"""
        data = urllib2.urlopen(url, xml, timeout=second).read()
        return data

    def postXmlSSL(self, xml, url, second=30):
        """使用证书"""
        raise TypeError("please use CurlClient")


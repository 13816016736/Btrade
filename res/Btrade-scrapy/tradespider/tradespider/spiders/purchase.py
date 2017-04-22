#coding:utf8
import scrapy
from scrapy.http import Request, FormRequest
import json
from scrapy.selector import Selector
from tradespider.items import PurchaseItem

class purchaseSpider(scrapy.Spider):
    name = 'purchaseSpider'
    allowed_domains = ['zyctd.com']
    login_url = 'https://secure.zyctd.com/Ajax/AjaxHandle.ashx?CommandName=UserSignService/SignIn'
    info_url="http://www.zyctd.com/gqqg/"


    def start_requests(self):
        mydata ={
        "LoginName": "13638654365",
        "Password": "19880323",
        "IsNeedCheckCode": "False",
        "CheckCode":""
        }
        return [FormRequest(self.login_url,
                                   formdata={
                                       "Data": json.dumps(mydata)
                                   },
                                   callback=self.login)]

    # 登录
    def login(self, response):

        result=json.loads(response.body_as_unicode())
        if result["ErrorCode"]==0:
            #登录成功
            yield scrapy.FormRequest(
                url=self.info_url,
                callback=self.parse
            )

    #分析页面
    def parse(self, response):
        selector = Selector(response)
        trs=selector.xpath(u"//tr[not(@class='check_content')]")
        extra = selector.xpath(u"//tr[@class='check_content']/td[@colspan='2']/text()").extract()
        index=0
        for tr in trs:
            item = PurchaseItem()
            tds=tr.xpath(u".//td/text()").extract()
            if(len(tds)>7):
                item["variety"] = tds[0]
                item["spec"] = tds[1]
                item["quantity"] = tds[2]
                item["origin"] = tds[2]
                item["name"]= tds[3]
                item["mobile"] =  tds[4]
                item["origin"] = tds[5]
                item["purchaseDate"]=tds[6]
                item["quality"]=extra[index]
                index+=1
                yield item
        now = selector.xpath(u"//span[@class='now numBtn']/text()").extract()
        if(len(now)!=0):
            pageNow=int(now[0])
            pageNext=selector.xpath(u"//a[@class='page'][contains(text(),'下一页')]/text()").extract()
            if (len(pageNext)!=0):
                yield scrapy.FormRequest(
                    url="http://www.zyctd.com"+"/gqqg/0-0-p"+str(pageNow+1)+".html",
                    callback=self.parse
                )




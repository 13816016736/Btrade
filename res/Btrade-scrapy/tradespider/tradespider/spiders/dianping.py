#coding:utf8
import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
from tradespider.items import StoreItem

class DianSpider(scrapy.Spider):
    name = "dianping"
    allowed_domains = ["www.dianping.com"]
    start_urls = [
        u"http://www.dianping.com/search/keyword/16/85_%E4%B8%AD%E5%8C%BB%E8%AF%8A%E6%89%80"
    ]

    detail_url="http://www.dianping.com"


    def parse(self, response):
        selector = Selector(response)
        trs=selector.xpath(u"//a[@data-hippo-type='shop']/@href")
        for tr in trs:
            yield Request(url=self.detail_url+tr.extract(), callback=self.catch_item)

        cur=selector.xpath(u"//div[@class='page']/a[@class='cur']/text()").extract()
        next=selector.xpath(u"//div[@class='page']/a[@class='next']").extract()
        nextlink=self.start_urls[0]+"/p"+str(int(cur[0])+1)
        if next!=[]:
          yield Request(nextlink, callback=self.parse)




    @staticmethod
    def catch_item(response):
        selector = Selector(response)
        item = StoreItem()
        item["name"]=selector.xpath(u"//h1[@class='shop-name']/text()").extract()[0]
        item["address"] = selector.xpath(u"//span[@itemprop='street-address']/text()").extract()[0]
        mobile=selector.xpath(u"//span[@itemprop='tel']/text()")
        if mobile!=[]:
            item["mobile"] =mobile.extract()[0]
        else:
            item["mobile"] =""

        return item
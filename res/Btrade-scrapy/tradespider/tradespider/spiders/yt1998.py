import scrapy
from scrapy.http.request import Request
from scrapy.selector import Selector
from tradespider.items import Yt1998Item

class Yt1998Spider(scrapy.Spider):
    name = "yt1998"
    allowed_domains = ["yt1998.com"]
    start_urls = [
        "http://www.yt1998.com/supplyInfo.html"
    ]

    def parse(self, response):
        selector = Selector(response)
        selectLine1hrefs = selector.xpath('//div[@class="fl pr"]/a/@href').extract()
        print "++++"
        print selectLine1hrefs
        print "++++"
        for url in selectLine1hrefs:
            url = "www.yt1998.com" + url
            print "-----"
            print url
            # request = Request(url=url, callback=lambda response, typeid=1: self.catch_item(response, typeid))
            # yield request

        # selectLine2 = selector.xpath('//div[@class="headline"]/div[@class="selectLine2"]').extract()
        # typeid = 1
        # for selectLine in selectLine2:
        #     typeid += 1
        #     selectLine2hrefs = selector.xpath('//div[@class="headline"]/div[@class="selectLine2"][' + str(typeid - 1) + ']/div[@class="proRight"]/ul/li/a/@href').extract()
        #     for url in selectLine2hrefs:
        #         url = "http://www.yaocai.com" + url
        #         print "-----"
        #         print url
        #         request = Request(url=url, callback=lambda response, typeid=typeid: self.catch_item(response, typeid))
        #         yield request

    @staticmethod
    def catch_item(response, typeid):
        selector = Selector(response)
        item = Yt1998Item()
        return item
